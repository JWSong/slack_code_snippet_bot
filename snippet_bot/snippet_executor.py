import logging
import subprocess
import tempfile

from config import TIMEOUT

logger = logging.getLogger(__name__)


class SnippetExecutor(object):

    def __init__(self, code, lang, user_input):
        self.code = code
        self.lang = lang
        self.status = 0
        self.input = user_input

    def __enter__(self):
        suffix = self.lang == 'c' and '.c' or self.lang == 'cpp' and '.cpp' or '.py'

        self.temp_file = tempfile.NamedTemporaryFile(mode='w+b', suffix=suffix)
        self.temp_file.write(self.code)
        self.temp_file.seek(0)

        executable = self.temp_file.name + '.out'

        if self.lang == 'python':
            cmds = [['python', self.temp_file.name]]
        elif self.lang == 'cpp':
            cmds = [['g++', self.temp_file.name, '-o', executable],
                    [executable]]
        elif self.lang == 'c':
            cmds = [['gcc', self.temp_file.name, '-o', executable],
                    [executable]]
        else:
            cmds = []

        try:
            logger.debug(cmds)
            for args in cmds:
                output = subprocess.check_output(
                    args, input=self.input, universal_newlines=True, stderr=subprocess.STDOUT, timeout=TIMEOUT
                )
        except subprocess.CalledProcessError as e:
            output = e.output
            self.status = 1
        except subprocess.TimeoutExpired as e:
            output = "timed out after {0:d} seconds".format(TIMEOUT)
            self.status = 1

        logger.debug(output)
        return output, self.status

    def __exit__(self, *args):
        self.temp_file.close()
