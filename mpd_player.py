import logging
import subprocess

log = logging.getLogger(__name__)


class Player:

    def load_list(self, list_dir):
        self.mpc_command('clear')
        self.mpc_command('mpc ls {} | mpc --wait add'.format(list_dir), custom_command=True)
        result = self.mpc_command('playlist')
        log.info(result)

    def play(self):
        self.mpc_command('play')
        self.current()

    def next(self):
        self.mpc_command('next')
        self.current()

    def prev(self):
        self.mpc_command('prev')
        self.current()

    def stop(self):
        self.mpc_command('stop')

    def pause(self):
        self.mpc_command('pause')

    def toggle(self):
        self.mpc_command('toggle')
        self.current()

    def current(self):
        result = self.mpc_command('mpc current', custom_command=True)
        log.info(result)

    def is_playing(self):
        result = self.mpc_command('mpc status | awk \'NR==2\'', custom_command=True)
        return 'playing' in result

    @staticmethod
    def update():
        Player.mpc_command('update')

    @staticmethod
    def mpc_command(command, custom_command=False):
        if not custom_command:
            mpc_prefix = 'mpc -q --wait'
            mpc_command = ' '.join([mpc_prefix, command])
        else:
            mpc_command = command
        result = subprocess.check_output(mpc_command, shell=True)
        return result.decode('utf8')
