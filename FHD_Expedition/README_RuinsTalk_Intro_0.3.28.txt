FHD_Expedition v0.3.28 — RuinsTalk Intro Request Fix

Что исправлено относительно 0.3.27:
- Сохранена схема диалога по пользовательскому скриншоту:
  * описание экспедиции появляется в верхнем штатном поле RuinsTalk;
  * ответы «Продолжить» и «Отказаться» появляются в нижнем штатном списке ответов;
  * отдельное окно не используется.
- Исправлен вылет TBlockParEC.Block_Get: в Lang.dat зарегистрирован скрытый служебный тип
  ShipInfo/AddInfo/CustomInfos/FHDExpeditionIntroRequest.
- Тип скрытый (Description=NoShow), используется только как одноразовый флаг для перехода
  из нижней кнопки Expeditions в штатный диалог базы и сразу удаляется.
- Основной FHD_Expedition.scr, вспомогательный FHD_Expedition_Intro.scr,
  FHDExpeditionNative.dll, Main.dat и CacheData.dat относительно 0.3.27 не изменены.
