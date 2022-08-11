del wmm.apk
del wmm-aligned-debugSigned.apk

copy "C:\Users\christineka\Documents\android\wmw level editor\wmw-level-editor\src\game\wmp\dist\wmw.apk" "wmw.apk"

java -jar uber-apk-signer.jar --apks wmw.apk

adb uninstall com.disney.WMW

adb install wmw-aligned-debugSigned.apk