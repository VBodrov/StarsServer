import configparser

# TODO: Setup script to use this code
config = configparser.ConfigParser(allow_no_value=True)

""" Paths """
config.add_section('PATHS')
config.set('PATHS', '; Root directory for StarsServer')
config.set('PATHS', 'ROOT', '')

config.set('PATHS', '; Path to Stars! exe-file')
config.set('PATHS', 'EXE', '')

config.set('PATHS', '; Launcher statement:')
config.set('PATHS', '; for Win path to otvdm')
config.set('PATHS', '; for Linux path to wine')
config.set('PATHS', 'LAUNCHER', '')

config.set('PATHS', '; Path to backup folder. It will override Stars! backup algorithms')
config.set('PATHS', 'BACKUP', '')

config.set('PATHS', '; Path to actual game-files manipulations. Should be allowed only to host')
config.set('PATHS', 'CRADLE', '')

config.set('PATHS', '; Path to exchange directory. StarsServer will fetch .xN files, and put .mN files here')
config.set('PATHS', '; Files from here is save to open by players')
config.set('PATHS', '; This directory behave same as Stars! folder. Or you could use other software to send files')
config.set('PATHS', 'EXCHANGE', '')

config.set('PATHS', '; Path for starmapper to generate beautiful map. Not implemented thou')
config.set('PATHS', 'MAP', '')

config.set('PATHS', '; Starmapper and StarMerger goes here')
config.set('PATHS', 'UTILS', '')

config.set('PATHS', '; Not implemented yet')
config.set('PATHS', 'IMAGEMAGICK', '')

config.set('PATHS', '; Path to stars.ini. Just in case, not using it for now')
config.set('PATHS', 'STARSCONFIG', '')

""" Bot parameters"""

config.add_section('BOT')
config.set('BOT', '; This section could be ignored, if TelegramBot not in use')
config.set('BOT', '; TG_TOKEN - given by BotFather')
config.set('BOT', 'TG_TOKEN', '')

config.set('BOT', '; Group for updates of new turn')
config.set('BOT', 'GROUP ID', '')

""" Game parameters"""

config.add_section('GAME')
config.set('GAME', '; Name of game-files')
config.set('GAME', 'NAME', '')

config.set('GAME', '; This is service variable, and will update as soon as new turn will be generated')
config.set('GAME', '; 2400 by default, but could be set according to game you are automating')
config.set('GAME', 'YEAR', '2400')

config.set('GAME', '; Number of players. May be deprecated later')
config.set('GAME', 'PLAYERS', '')

config.set('GAME', '; Service variable. Needed to generate new turn, despite submitted turns each 24 hour')
config.set('GAME', 'LAST TURN', '0')

config.set('GAME', '; When should StarsServer will generate new turn.')
config.set('GAME', '; If turn have been made in 24 hour period will pass. Set in local time.')
config.set('GAME', 'FORCE TURN', '06:00')

config.set('GAME', '; Until true will check for user inputs and operates as usual. Set to False for next game setup.')
config.set('GAME', 'ACTIVE', '')

config.set('GAME', '; .hst password')
config.set('GAME', 'PASSWORD', '')

""" Player section """

config.add_section('PLAYER1')
config.set('PLAYER1', '; Could be: PLAYER - for active players')
config.set('PLAYER1', '; INACTIVE - for inactive players')
config.set('PLAYER1', '; AI - for AI player')
config.set('PLAYER1', '; DEAD - well...')
config.set('PLAYER1', 'ROLE', '')

config.set('PLAYER1', '; Will be used to generate map and link with Telegram StarsBot')
config.set('PLAYER1', 'NAME', '')


config.set('PLAYER1', '; Password to m-file. Needed to generate map')
config.set('PLAYER1', 'PASSWORD', '')

config.set('PLAYER1', '; For StarsBot integration, trlrgram_id of this player')
config.set('PLAYER1', 'TG_ID', '')

config.set('PLAYER1', '; For StarsBot integration, telegram nick for sending updates')
config.set('PLAYER1', 'TG_NAME', '')

for i in range(2, 17):
    config.add_section('PLAYER' + str(i))
    config.set('PLAYER' + str(i), 'ROLE', '')
    config.set('PLAYER' + str(i), 'NAME', '')
    config.set('PLAYER' + str(i), 'PASSWORD', '')
    config.set('PLAYER' + str(i), 'TG_ID', '')
    config.set('PLAYER' + str(i), 'TG_NAME', '')

with open('StarsServer.ini', 'w') as configfile:
    config.write(configfile)
