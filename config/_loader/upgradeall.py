# -*- coding: utf-8 -*-
'''
Created on 2016年7月27日

@author: zqh
'''
from _loader import mainconf
import os
from _loader.mainhelper import ftlog


def clean(module):
    code = '''
try:
    from _loader.game5_9999.mname import clean
    clean.main()
except:
    pass
'''
    code = code.replace('mname', module)
    exec code


def upgrade(base, module):
    code = '''
try:
    from _loader.game5_9999.mname import clean
    clean.main()
except:
    pass
from _loader.game5_9999.mname import upgrade
upgrade.main('%s/game/9999/mname/tc.json')
''' % (base)
    code = code.replace('mname', module)
#     print code
    exec code

if __name__ == '__main__':
    os.path.dirname(__file__)
    base = os.path.dirname(__file__) + './../../../hall37-onlines/config/'
    base = os.path.abspath(base)
    mainbasefile = base + '/game/tc.json'
    mainconf.init(mainbasefile)

    clean('condition')
    clean('todotask')

    upgrade(base, 'activity')
    upgrade(base, 'ads')
    upgrade(base, 'free')
    upgrade(base, 'item')
    upgrade(base, 'login_reward')
    upgrade(base, 'popwnd')
    upgrade(base, 'products')
    upgrade(base, 'promote')
    upgrade(base, 'ranking')
    upgrade(base, 'roulette')
    upgrade(base, 'share')
    upgrade(base, 'store')
    upgrade(base, 'storebuy')
    upgrade(base, 'tasks')

    ids = set()
    from _loader.game5_9999.todotask import uptodotasks
    uptodotasks.todoref.upgradeInit()
    for t in uptodotasks.todoref._TODOMAP.values():
        if 'typeId' in t :
            ids.add(t['typeId'])
            # ftlog.info('TODOTASK TYPEID->', t['typeId'])
        else:
            ids.add('templateName:' + t['templateName'])
            # ftlog.info('TODOTASK TEMPLATE->', t['templateName'])
    ids = list(ids)
    ids.sort()
    for x in ids :
        ftlog.info('TODOTASK TYPEID->', x)
    
    ids = set()
    from _loader.game5_9999.condition import upconditions
    upconditions.conref.upgradeInit()
    for t in upconditions.conref._TODOMAP.values():
        ids.add( t['typeId'])
        # ftlog.info('CONDICTION TYPEID->', t['typeId'])
    ids = list(ids)
    ids.sort()
    for x in ids :
        ftlog.info('CONDICTION TYPEID->', x)
