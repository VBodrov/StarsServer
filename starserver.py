import subprocess
import time
import os
import configparser
import shutil
import glob
import logging

logging.basicConfig(level=logging.INFO,  # TODO: Clean logging information
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

#  Config structure described in create_config.py TODO: Setup script for new game
config = configparser.ConfigParser()
try:
    config.read('StarsServer.ini')
    logger.info('ini-file loaded')
except IOError:
    logger.error("Couldn't read StarsServer.ini")


def force_turn():
    """ Function for force turn, despite submitted turns """

    cmd = config['PATHS']['LAUNCHER'] + " " + config['PATHS']['EXE'] + " -g " + config['PATHS']['CRADLE'] \
        + config['GAME']['NAME'] + ".hst" \
        + " -l -p " + config['GAME']['PASSWORD']
    try:
        subprocess.check_output(cmd, shell=False, timeout=10)
    except subprocess.TimeoutExpired:
        logger.error("Couldn't force generate turn. Timeout")
        return False
    else:
        log = config['PATHS']['CRADLE'] + config['GAME']['NAME'] + '.log'
        if os.path.exists(log):
            os.remove(log)
            logger.info('Force turn generated')
            return True
        else:
            logger.error("force_turn() couldn't force generate turn. No .log file")
            return False


def try_turn():
    """ This function will try to generate new turn if every player submitted their turns
    But may be deprecated, couse we check state of x-files anyway """

    cmd = config['PATHS']['LAUNCHER'] + " " + config['PATHS']['EXE'] + " -t -g " + config['PATHS']['CRADLE'] \
        + config['GAME']['NAME'] + ".hst" \
        + " -l -p " + config['GAME']['PASSWORD']
    try:
        subprocess.check_output(cmd, shell=False, timeout=10)
    except subprocess.TimeoutExpired:
        logger.error("Couldn't generate turn. Timeout")
        return False
    else:
        log = config['PATHS']['CRADLE'] + config['GAME']['NAME'] + '.log'
        if os.path.exists(log):
            os.remove(log)
            logger.info('Turn generated')
            return True
        else:
            logger.error("try_turn() couldn't generate turn. No .log file")
            return False


def verify_turn():
    """ This function does two things:
    1) It will autogenerate x-files for inactive and dead players
    2) It will update player state if host set them inactive or they, well, dead """

    cmd = config['PATHS']['LAUNCHER'] + " " + config['PATHS']['EXE'] + " -v " + config['PATHS']['CRADLE'] \
        + config['GAME']['NAME'] + ".hst" \
        + " -l -p " + config['GAME']['PASSWORD']
    try:
        subprocess.check_output(cmd, shell=False, timeout=10)
    except subprocess.TimeoutExpired:
        logger.error("Couldn't check turn. Timeout")
        return False
    else:
        try:
            chk = config['PATHS']['CRADLE'] + config['GAME']['NAME'] + '.chk'
            file = open(chk, 'r')
            content = file.readlines()
            file.close()
            os.remove(chk)
            status = content[2]
            if status[20:25] != 'Error':
                logger.info('Turn ' + status[len(status)-5:len(status)-1] + ' have been checked')
                player_n = 0
                for line in content[3:]:
                    player_n += 1
                    if line.find('dead') >= 0 and config['PLAYER' + str(player_n)]['ROLE'].upper() != 'DEAD':
                        config.set('PLAYER' + str(player_n), 'ROLE', 'DEAD')
                        save_config()
                        logger.info('Player' + str(player_n) + ' have been defeated. Status updated')
                return True
            else:
                logger.error(status[20:])  # Only error message i could get is invalid password
                return False
        except IOError:
            logger.error("Couldn't check turn. No .chk file")
            return False


def check_submitted(player_number):
    """ This function will check if player_number have submitted his turn """

    x_file = config['PATHS']['CRADLE'] + config['GAME']['NAME'] + ".x" + str(player_number)
    try:
        file = open(x_file, 'rb')
    except IOError:
        logger.error("Couldn't open .x" + str(player_number) + " file")
        return False
    else:
        with file:
            byte = file.read(18)
            if byte[17] & 0x01:
                logger.info('Player ' + str(player_number) + ' submitted his turn')
                return True
            else:
                return False


def turn_year(hst_file):
    """ This function checks .hst-file turn. It could be actually any Stars! file """
    try:
        file = open(hst_file, 'rb')
    except IOError:
        logger.error("Couldn't open " + str(hst_file) + " file")
        return False
    else:
        with file:
            byte = file.read(13)
            return byte[12] + int(2400)


def check_year(player_number):
    """ This function checks if .hst and .x files is at same year """
    hst_file = config['PATHS']['CRADLE'] + config['GAME']['NAME'] + ".hst"
    x_file = config['PATHS']['CRADLE'] + config['GAME']['NAME'] + ".x" + str(player_number)

    if turn_year(hst_file) == turn_year(x_file):
        logger.info("Player " + str(player_number) + " is up to date")
        return True
    else:
        logger.info("Player " + str(player_number) + " is outdated")
        return False


def merge_m(player_list):
    """ If game have predefined alliance this function will share their intel
    TODO: add functionality to define alliances in running game """

    cmd = 'java -jar ' + config['PATHS']['UTILS'] + 'StarsFileMerger.jar -m '
    for player_n in player_list:
        cmd += config['PATHS']['CRADLE'] + config['GAME']['NAME'] + '.m' + str(player_n) + ' '

    status = subprocess.check_output(cmd)

    if status:  # StarsFileMerger will not output anything is have been completed successful
        logging.error('.m-files have not been merged')
        return False
    else:
        logging.info('.m-files have been merged')  # TODO: add backup-m files existence test to be sure
        return True


def dump_map(player_number):
    """ Will dump .map file to generate map later. TODO: use this function at setup script """

    cmd = config['PATHS']['LAUNCHER'] + " " + config['PATHS']['EXE'] + " -dm " + config['PATHS']['CRADLE'] \
        + config['GAME']['NAME'] + ".m" + str(player_number) \
        + " -l -p " + config['PLAYER' + str(player_number)]['PASSWORD']
    try:
        subprocess.check_output(cmd, shell=False, timeout=10)
    except subprocess.TimeoutExpired:
        logger.error('Dump .map file timed out')
        return False
    else:
        if os.path.exists(config['PATHS']['CRADLE'] + config['GAME']['NAME'] + '.map'):
            logging.info('.map file dumped successfully')
            return True
        else:
            logging.error(".map file haven't dumped")
            return False


def dump_pla(player_number):
    """ This function dump .pN files, and do this every turn for active player. Will be used to generate map.
    Could be used to generate map manually """

    cmd = config['PATHS']['LAUNCHER'] + " " + config['PATHS']['EXE'] + " -dp " + config['PATHS']['CRADLE'] \
        + config['GAME']['NAME'] + ".m" + str(player_number) \
        + " -l -p " + config['PLAYER' + str(player_number)]['PASSWORD']
    try:
        subprocess.check_output(cmd, shell=False, timeout=10)
    except subprocess.TimeoutExpired:
        logging.error('Dump .p' + str(player_number) + ' failed')
        return False
    else:
        if os.path.exists(config['PATHS']['CRADLE'] + config['GAME']['NAME'] + ".p" + str(player_number)):
            logging.info('.p' + str(player_number) + ' file dumped successfully')
            return True
        else:
            logging.error(".p" + str(player_number) + " file haven't dumped")
            return False


def exchange_m_files(player_number):
    """ Will send newly generated .m-files to exchange folder for further logistics and delete outdated .x-files
    to imitate vanilla-Stars! behavior so players could share one folder without access to .hst file """

    shutil.copyfile(config['PATHS']['CRADLE'] + config['GAME']['NAME'] + '.m' + str(player_number),
                    config['PATHS']['EXCHANGE'] + config['GAME']['NAME'] + '.m' + str(player_number))

    if os.path.exists(config['PATHS']['EXCHANGE'] + config['GAME']['NAME'] + '.m' + str(player_number)):
        if os.path.exists(config['PATHS']['EXCHANGE'] + config['GAME']['NAME'] + '.x' + str(player_number)):
            os.remove(config['PATHS']['EXCHANGE'] + config['GAME']['NAME'] + '.x' + str(player_number))
            logger.info("Exchange for player " + str(player_number) + " have been successful.")
            logger.info("m-files updated, x-files deleted")
            return True
        else:
            logger.info("Exchange for player " + str(player_number) + " have been successful.")
            return True
    else:
        logger.error("Exchange for player " + str(player_number) + " failed")
        return False


def exchange_x_files(player_number):
    """ This function fetch .x-files from exchange folder. It is safe to grab them as they appear, cause
    they verify both on submission and outdated """

    if os.path.exists(config['PATHS']['EXCHANGE'] + config['GAME']['NAME'] + '.x' + str(player_number)):
        shutil.copyfile(config['PATHS']['EXCHANGE'] + config['GAME']['NAME'] + '.x' + str(player_number),
                        config['PATHS']['CRADLE'] + config['GAME']['NAME'] + '.x' + str(player_number))
        logger.info('.x files for player ' + str(player_number) + ' fetched successfully')
        return True
    else:
        logger.error("Couldn't fetch .x-file for player " + str(player_number))
        return False


def make_map(player_list):
    """ TODO: implement this function
    This function copy .pX files in starmapper fashion for each active player to make map.
    This makes sense only for predefined alliances. See above: merge_m(player_list) """
    for n in player_list:
        dump_pla(n)
        try:
            shutil.copyfile(config['PATHS']['CRADLE'] + config['GAME']['NAME'] + '.p' + str(n),
                            config['PATHS']['MAP'] + 'pla\\' + config['GAME']['NAME']
                            + ' ' + config['GAME']['YEAR'] + '.p' + str(n))
        except IOError:
            logger.error("Couldn't make map")
            return False
        else:
            logger.info('.pX files copied successfully')

    #  Block for starmapper call and verification
    logger.info('Map for current turn generated')
    return True


def backup():
    """ Function to copy all files for current turn, including .pX files and backups of .m-files after merging"""

    try:
        os.mkdir(config['PATHS']['BACKUP'] + config['GAME']['NAME'] + "_history")
        time.sleep(1)
    except IOError:
        logger.error('Backup folder already exist')  # This may be redundant code if setup script will be implemented

    try:
        shutil.move(config['PATHS']['CRADLE'] + 'backup',
                    config['PATHS']['BACKUP'] + config['GAME']['NAME'] + '_history\\' + config['GAME']['YEAR'])
    except IOError:
        logger.error('Backup folder not found or already moved')
    else:
        logger.info('Vanilla Stars! backup moved successfully')

    shutil.copyfile(config['PATHS']['CRADLE'] + config['GAME']['NAME'] + '.xy',
                    config['PATHS']['BACKUP'] + config['GAME']['NAME'] + '_history\\' + config['GAME']['YEAR']
                    + '\\' + config['GAME']['NAME'] + '.xy')
    logger.info('Added .xy file to backup folder, for easier access to archived turn')

    for f in glob.glob(config['PATHS']['CRADLE'] + '*backup*'):
        shutil.move(f, config['PATHS']['BACKUP'] + config['GAME']['NAME'] + '_history\\' + config['GAME']['YEAR']
                    + '\\' + f[len(config['PATHS']['CRADLE']):len(f)])
    logger.info('Backups of .m-files before merging moved successfully')

    for f in glob.glob(config['PATHS']['CRADLE'] + '*.p*'):
        shutil.move(f, config['PATHS']['BACKUP'] + config['GAME']['NAME'] + '_history\\' + config['GAME']['YEAR']
                    + '\\' + f[len(config['PATHS']['CRADLE']):len(f)])
    logger.info('Backups of .pN-files moved successfully')

    return True


def get_player_count():
    """ This function counts players still in play """
    player = []

    for player_n in range(1, int(config['GAME']['PLAYERS']) + 1):
        if config['PLAYER' + str(player_n)]['ROLE'].upper() == 'PLAYER':
            player.append(player_n)

    logger.info('There is Players: ' + str(player) + ' curently in game')
    return player


def time_save(time_to_save):
    """ Save time of last turn in ini-file for save state purposes """

    config.set('GAME', 'LAST TURN', str(time_to_save))
    if save_config():
        logger.info('Time of last turn have been saved')
        return True
    else:
        logger.error("Couldn't update ini-file")
        return False


def year_save():
    """ Save turn year for save state purposes """

    config.set('GAME', 'YEAR', str(turn_year(config['PATHS']['CRADLE'] + config['GAME']['NAME'] + ".hst")))
    if save_config():
        logger.info('Turn year have been saved')
        return True
    else:
        logger.error("Couldn't update ini-file")
        return False


def save_config():
    """ Function to save updated config file"""

    try:
        with open('StarsServer.ini', 'w') as configfile:
            config.write(configfile)
    except IOError:
        return False
    else:
        configfile.close()
        return True


if __name__ == "__main__":
    config.read('StarsServer.ini')
    t_turn = float(config['GAME']['LAST TURN'])
    t_turn_lt = time.localtime(t_turn)
    logger.info("Last turn time {:s}".format(time.strftime("%Y.%m.%d-%H:%M:%S", t_turn_lt)))

    while config['GAME']['ACTIVE'] == 'True':
        config.read('StarsServer.ini')
        t = time.time()
        t_lt = time.localtime(t)

        players_ready = 0

        players = get_player_count()
        for i in players:
            exchange_x_files(i)
            check_submitted(i)
            check_year(i)

            if check_year(i) and check_submitted(i):
                players_ready += 1
            
        # Check if ready
        if players_ready == len(players):
            verify_turn()  # Очень странное поведение Stars! когда если игрок не активен,
            # нужно запустить верификацию, чтобы автоматически сгенерился X файл за выбывшего игрока.
            if try_turn():
                if merge_m(players):
                    make_map(players)
                    backup()
                    year_save()
                    t_turn = t
                    time_save(t)
                    for i in players:
                        exchange_m_files(i)
                verify_turn()  # И еще раз, чтобы убрать из расчетов мёртвых игроков.

        # Force turn
        force_turn_time = config['GAME']['FORCE TURN']
        force_turn_time = force_turn_time.split(':')

        if (t_lt.tm_hour >= int(force_turn_time[0])) & (t_lt.tm_min >= int(force_turn_time[1])):
            if (t - t_turn) > 60*60*24-60:  # one day timeout = 60*60*24-60
                if force_turn():
                    if merge_m(players):
                        make_map(players)
                        backup()
                        year_save()
                        t_turn = t
                        time_save(t)
                        for i in players:
                            exchange_m_files(i)
                    verify_turn()  # Checking for dead players

        t = time.time()
        time.sleep(10 - t % 10)
