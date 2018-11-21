import os
import subprocess
import logging

import svn.config
import svn.exception

_LOGGER = logging.getLogger(__name__)


class CommonBase(object):
    def external_command(self, cmd, success_code=0, do_combine=False,
                         return_binary=False, environment={}, wd=None):
        _LOGGER.debug("RUN: %s" % (cmd,))

        env = os.environ.copy()
        env['LANG'] = svn.config.CONSOLE_ENCODING
        env.update(environment)

        # p = subprocess.Popen(
        #     cmd,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.STDOUT,
        #     cwd=wd,
        #     env=env)
        try:
            p = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                cwd=wd,
                env=env)
            stdout = p.stdout.read()
            r = p.wait()
            p.stdout.close()

            with open('logs/log.log', 'a+', encoding='utf-8') as f1:
                f1.writelines('subprocess.Popen cmd :{}  r:{}！{}'.format(cmd, r, '\n'))

            if r != success_code:
                with open('logs/log.log', 'a+', encoding='utf-8') as f1:
                    f1.writelines('subprocess.Popen cmd  r :{}！\n'.format(r))
                raise svn.exception.SvnException(
                    "Command failed with ({}): {}\n{}".format(
                        p.returncode, cmd, stdout))

            if return_binary is True or do_combine is True:
                return stdout
        except Exception as e:
            with open('logs/log.log', 'a+', encoding='utf-8') as f1:
                f1.writelines('subprocess.Popen Exception cmd:{} :{}  cwd{}！\n'.format(cmd[2], e, wd))

        return stdout.decode(svn.config.CONSOLE_ENCODING).strip('\n').split('\n')

    def rows_to_dict(self, rows, lc=True):
        d = {}
        for row in rows:
            row = row.strip()
            if not row:
                continue

            pivot = row.index(': ')

            k = row[:pivot]
            v = row[pivot + 2:]

            if lc is True:
                k = k.lower()

            d[k] = v

        return d
