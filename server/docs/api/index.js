const _0x4d9116=_0x24f1;function _0x362a(){const _0x25eb68=['20631YWdAKv','380JnZMlL','12612gXtTle','./connect-AT','18NTMEda','12HfeQHl','./stop-log','73288FTqLqy','./disconnect-diag','116026XiollV','./process-log','764414fkMyON','./send-AT','376800MfnZWR','343856DINgqg','./disconnect-AT','95GYUoXJ','9tlBPmG','109978sPjmwI'];_0x362a=function(){return _0x25eb68;};return _0x362a();}function _0x24f1(_0x5a28,_0x29da10){const _0x362a7f=_0x362a();return _0x24f1=function(_0x24f191,_0x516aea){_0x24f191=_0x24f191-0xe6;let _0x146875=_0x362a7f[_0x24f191];return _0x146875;},_0x24f1(_0x5a28,_0x29da10);}(function(_0x1bbef8,_0xb61003){const _0x4b6202=_0x24f1,_0x3589c4=_0x1bbef8();while(!![]){try{const _0x2dd048=-parseInt(_0x4b6202(0xf1))/0x1*(parseInt(_0x4b6202(0xed))/0x2)+-parseInt(_0x4b6202(0xf5))/0x3+-parseInt(_0x4b6202(0xef))/0x4*(parseInt(_0x4b6202(0xf8))/0x5)+parseInt(_0x4b6202(0xec))/0x6*(parseInt(_0x4b6202(0xf3))/0x7)+parseInt(_0x4b6202(0xf6))/0x8*(-parseInt(_0x4b6202(0xe6))/0x9)+parseInt(_0x4b6202(0xe9))/0xa*(-parseInt(_0x4b6202(0xe7))/0xb)+-parseInt(_0x4b6202(0xea))/0xc*(-parseInt(_0x4b6202(0xe8))/0xd);if(_0x2dd048===_0xb61003)break;else _0x3589c4['push'](_0x3589c4['shift']());}catch(_0x2db9a1){_0x3589c4['push'](_0x3589c4['shift']());}}}(_0x362a,0x6254b));const connectDiag=require('./connect-diag'),disconnectDiag=require(_0x4d9116(0xf0)),startLog=require('./start-log'),stopLog=require(_0x4d9116(0xee)),processLog=require(_0x4d9116(0xf2)),getLog=require('./get-log'),connectAT=require(_0x4d9116(0xeb)),disconnectAT=require(_0x4d9116(0xf7)),sendAT=require(_0x4d9116(0xf4));module['exports']={'paths':{'/api/diag':{...connectDiag},'/api/diag/{id}':{...disconnectDiag},'/api/logs':{...startLog},'/api/logs/{log_id}':{...stopLog},'/api/logs/{log_id}/process':{...processLog,...getLog},'/api/AT':{...connectAT},'/api/AT/{id}':{...disconnectAT,...sendAT}}};