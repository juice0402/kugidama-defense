# index.html に、テスト用の窓口 window.__T を足した game.html を作る（dev/sim の中に）
import os
here=os.path.dirname(os.path.abspath(__file__))
src=open(os.path.join(here,'..','..','index.html'),encoding='utf-8').read()
i=src.rfind('})();')
names="G,update,startStage,setupStage,playBoard,BOARDS,STAGES,ENEMIES,TOWERS,BALLS,GIMMICKS,ELEM,COMBO,SPECIAL,openHub,spawn,addEnemy,popOut,stageOpen,draw,resize,buildStatic,towerHit,launch,openInfo,openBuild,closeSheet,showTab,stageClear,newTower,curEff,applyEff,comboOf,spOf,EL_ORDER,TLOCK,OBJK,ZONES,FXK,BULLETK,boardState,openBoardBuy,buyBoard,renderTab,openHub,towerHit,hurtEnemy,applyEl,applyCombo,applySpecial,fireBullet,finishHooks,HONEY,ROOT,MUSH,NUT,GM,HP_GROW,CANDLE,BAT,ARMOR,FLAP,HOWL,MIRROR,WARP,NEKO,flinch,confuse,BOSS_HOLD,BOSS_RES,bossGuard,MIA,TOKAGE,RAKUDA,SASORI,SPHINX,SAND,TWISTER,ARI,TORNADO,OKOJO,PENGUIN,TONAKAI,SEIUCHI,MAMMOTH,SNOW,CRYST,ICICLE,JUMP,SANDAN,aimAt,shatter,crystOn,snowOn,BUTA,HINO,SAI,INO,DRAGON,MAGMA,BOMB,FOUNT,HOUDAN,FUNKA,bombOn,magmaOn,funkaErupt,VOLC_P"
hook="window.__T={};for(const k of '%s'.split(',')){try{window.__T[k]=eval(k)}catch(_){}}\n"%names
open(os.path.join(here,'game.html'),'w',encoding='utf-8').write(src[:i]+hook+src[i:])
print('game.html ok')
