#!/usr/bin/env python

#http://gerrit-documentation.googlecode.com/svn/Documentation/2.2.2/cmd-query.html

import subprocess
from datetime import datetime
import simplejson as json
import time
import tempfile
import os


class FGerrit(object):

    def __init__(self, ssh_user, ssh_host, project, ssh_port=29418,
                 status="open"):
        self.ssh_user = ssh_user
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.project = project
        self.status = status

    def _conv_ts(self, timestamp, terse=False):
        if terse:
            when = time.time() - timestamp
            if when < 60:
                return '%4.1fs' % when
            elif when < 3600:
                return '%4.1fm' % (when / 60)
            elif when < 86400:
                return '%4.1fh' % (when / 3600)
            else:
                return '%4.1fd' % (when / 86400)
        else:
            return datetime.fromtimestamp(int(timestamp))

    def _run_query(self, qargs, plain=False):
        if not plain:
            sshcmd = 'ssh -p %d %s@%s "gerrit query --format=JSON %s"' % \
                        (self.ssh_port, self.ssh_user, self.ssh_host, qargs)
        else:
            sshcmd = 'ssh -p %d %s@%s "gerrit query --format=TEXT %s"' % \
                        (self.ssh_port, self.ssh_user, self.ssh_host, qargs)
        p = subprocess.Popen(sshcmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        retval = p.wait()
        if retval != 0:
            raise Exception('Error on ssh to gerrit %s' % p.stdout.readlines())
        if not plain:
            result = []
            for line in p.stdout.readlines():
                result.append(json.loads(line))
            retval = p.wait()
            return [x for x in result if 'status' in x]
        else:
            return " ".join(p.stdout.readlines())

    def _run_cmd(self, cargs):
        sshcmd = "ssh -p %d %s@%s 'gerrit %s'" % (self.ssh_port, self.ssh_user, self.ssh_host, cargs.replace("'", "'\"'\"'"))
        p = subprocess.Popen(sshcmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        retval = p.wait()
        if retval != 0:
            raise Exception('Error on ssh to gerrit %s' % p.stdout.readlines())
        return " ".join(p.stdout.readlines())

    def list_reviews(self):
        return self._run_query('status:%s project:%s --current-patch-set' % (self.status,
                                                                             self.project))
    def _parse_approvals(self, review, detailed=False):
        if detailed:
            approvals = []
        else:
            approvals = {'VRIF': 0 , 'CRVW': 0, 'APRV': 0, 'SUBM': 0}
        if 'approvals' not in review['currentPatchSet']:
            return None
        for i in review['currentPatchSet']['approvals']:
            if i:
                if detailed:
                    if i:
                        approvals.append(i)
                else:
                    if i['value'] < 0:
                        if i['value'] < approvals[i['type']]:
                            approvals[i['type']] = i['value']
                    elif i['value'] > approvals[i['type']]:
                        approvals[i['type']] = i['value']
        return approvals

    def get_approvals(self, review_id, detailed=False):
        review = self._run_query('%s --current-patch-set' % review_id)
        return self._parse_approvals(self, review[0], detailed)

    def get_review(self, review_id, comments=False, text=False):
        """Either a short id (5264) or long hash"""
        if comments:
            return self._run_query('%s --current-patch-set --comments --commit-message' % review_id, plain=text)
        else:
            return self._run_query(review_id, plain=text)

    def delete_change(self, patchset):
        payload = "review %s --delete" % patchset
        return self._run_cmd(payload)

    def abandon_change(self, patchset):
        payload = "review %s --abandon" % patchset
        return self._run_cmd(payload)

    def publish_draft(self, patchset):
        payload = "review %s --restore" % patchset
        return self._run_cmd(payload)

    def restore_change(self, patchset):
        payload = "review %s --restore" % patchset
        return self._run_cmd(payload)

    def submit_change(self, patchset):
        payload = "review %s --submit" % patchset
        return self._run_cmd(payload)

    def post_message(self, review_id, message):
        if message == '-':
            editor = os.environ.get('FGERRIT_EDITOR', os.environ.get('EDITOR', 'vi'))
            with tempfile.NamedTemporaryFile() as fp:
                p = subprocess.Popen('%s %s' % (editor, fp.name), shell=True)
                retval = p.wait()
                if retval != 0:
                    raise Exception('Error on editor exit code %d' % retval)
                message = fp.read().strip()
        if not message:
            raise Exception('Abort, no message')
        payload = "review %s --message='%s'" % (review_id, message.replace("'", "'\"'\"'"))
        print payload
        print repr(payload)
        return self._run_cmd(payload)

    def verify_change(self, review_id, score, message=None):
        valid_scores = ["-1", "0", "+1"]
        if message:
            payload = "review %s --verified %s --message='%s'" % (review_id,
                                                                     score,
                                                                     message)
        else:
            payload = "review %s --verified %s" % (review_id, score)
        if score in valid_scores:
            return self._run_cmd(payload)
        else:
            raise Exception('Score should be one of: %s' % valid_scores.keys())

    def code_review(self, review_id, score, message=None):
        valid_scores = ["-2", "-1", "0", "+1", "+2"]
        if message:
            payload = "review %s --code-review %s --message='%s'" % (review_id,
                                                                     score,
                                                                     message)
        else:
            payload = "review %s --code-review %s" % (review_id, score)
        if score in valid_scores:
            return self._run_cmd(payload)
        else:
            raise Exception('Score should be one of: %s' % valid_scores.keys())

    def approve_review(self, review_id, score, message=None):
        valid_scores = ["0", "+1"]
        if message:
            payload = "approve %s --approve %s --message='%s'" % (review_id,
                                                                   score,
                                                                   message)
        else:
            payload = "approve %s --approve %s" % (review_id, score)
        if score in valid_scores:
            return self._run_cmd(payload)
        else:
            raise Exception('Score should be one of: %s' % valid_scores.keys())

    def print_reviews_list(self, reviews):
        title = "Open reviews for %s" % self.project
        tlen = len(title)
        id_header = "id%s" % (" "*(len(reviews[0]['number'])-2))
        header = '%s \t( when) [ V| C| A] "commit subject" - submitter' % \
                id_header
        print "=" * (len(header)+1)
        print "= %s%s =" % (title, " " * (len(header)-tlen-3))
        print "=" * (len(header)+1)
        print header
        print "-" * (len(header)+1)
        for r in reviews:
            scores = self._parse_approvals(r)
            if scores:
                print '%s\t(%s) [%02s|%02s|%02s] "%s" - %s' % (r['currentPatchSet']['revision'][:5],
                                                         self._conv_ts(r['lastUpdated'],
                                                                       terse=True),
                                                         scores['VRIF'],
                                                         scores['CRVW'],
                                                         scores['APRV'],
                                                         r['subject'],
                                                         r['owner']['name'])
            else:
                print '%s\t(%s) [  |  |  ] "%s" - %s' % (r['currentPatchSet']['revision'][:5],
                                                      self._conv_ts(r['lastUpdated'], terse=True),
                                                      r['subject'], r['owner']['name'])

    def print_review_comments(self, review):
        for comment in review[0]['comments']:
            print "="*25
            print "%s - %s:" % (self._conv_ts(comment['timestamp']),
                                comment['reviewer']['username'])
            print ""
            print comment['message']
            print ""


    def print_review(self, review_id):
        data = self.get_review(review_id, comments=True)[0]
        out = [('Owner', '%s <%s>' % (data['owner']['name'], data['owner']['username']))]
        if data['branch'] != 'master':
            out.append(('TARGETED BRANCH', data['branch']))
        out.extend([('Patch Set Number', data['currentPatchSet']['number']),
                    ('Patch Set Date', time.asctime(time.localtime(int(data['currentPatchSet']['createdOn'])))),
                    ('Patch Set Id', data['currentPatchSet']['revision'][:5])])
        approvals = []
        for approval in data['currentPatchSet'].get('approvals', []):
            approvals.append('%+d %s' % (int(approval['value']), approval['by']['username']))
        out.extend([('Status', ', '.join(sorted(approvals))),
                    ('Commit Message', data['commitMessage'].strip() + '\n')])
        for comment in data.get('comments', []):
            out.extend([('Reviewer', '%s <%s>' % (comment['reviewer']['name'], comment['reviewer']['username'])),
                        ('Date', time.asctime(time.localtime(int(comment['timestamp'])))),
                        ('Comment', comment['message'].strip() + '\n')])
        tlen = max(len(t) for t, v in out)
        for title, value in out:
            value = value.replace('\n', '\n' + (' ' * (tlen + 2)))
            print ('%%0%ds  %%s' % tlen) % (title, value)
