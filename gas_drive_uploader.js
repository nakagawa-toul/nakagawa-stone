/**
 * 中川石材 財務・資金繰り Googleドライブ自動同期 ＆ 請求書保存スクリプト (GAS)
 * 
 * 【主な機能】
 * 1. 資金繰り・口座残高・取引データの Google ドライブ自動保存 ＆ 自動読み込み (クラウド同期)
 * 2. 請求書写真の Google ドライブ「請求書 / YYYY年MM月」自動仕分け保存
 * 3. Mac・スマホ間で追加費用ゼロでのリアルタイムデータ同期
 */

var DATA_FILE_NAME = '中川石材_資金繰りデータ.json';

function doGet(e) {
  try {
    var action = (e && e.parameter && e.parameter.action) ? e.parameter.action : 'ping';

    // 1. データ読み込みリクエストの場合
    if (action === 'load_data') {
      var files = DriveApp.getFilesByName(DATA_FILE_NAME);
      if (files.hasNext()) {
        var file = files.next();
        var content = file.getBlob().getDataAsString();
        return ContentService.createTextOutput(JSON.stringify({
          success: true,
          data: JSON.parse(content),
          updatedAt: file.getLastUpdated().toISOString(),
          fileUrl: file.getUrl()
        })).setMimeType(ContentService.MimeType.JSON);
      } else {
        return ContentService.createTextOutput(JSON.stringify({
          success: true,
          data: null,
          message: '保存されたデータファイルはまだありません'
        })).setMimeType(ContentService.MimeType.JSON);
      }
    }

    // 2. 疎通テスト（Ping）の場合
    var rootFolder = getOrCreateFolder(DriveApp.getRootFolder(), '請求書');
    var result = {
      status: 'ok',
      message: '中川石材 Googleドライブ自動同期システムは正常に稼働しています。',
      rootFolderUrl: rootFolder.getUrl(),
      rootFolderName: rootFolder.getName(),
      dataFileExists: DriveApp.getFilesByName(DATA_FILE_NAME).hasNext(),
      timestamp: new Date().toISOString()
    };
    return ContentService.createTextOutput(JSON.stringify(result))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: 'error',
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var action = data.action || (data.base64Data ? 'upload_invoice' : 'save_data');

    // ----------------------------------------------------
    // A. 資金繰り・口座残高データの保存（クラウド自動同期）
    // ----------------------------------------------------
    if (action === 'save_data') {
      var payloadStr = JSON.stringify(data.payload || {}, null, 2);
      var files = DriveApp.getFilesByName(DATA_FILE_NAME);
      var dataFile;
      if (files.hasNext()) {
        dataFile = files.next();
        dataFile.setContent(payloadStr);
      } else {
        dataFile = DriveApp.createFile(DATA_FILE_NAME, payloadStr, MimeType.PLAIN_TEXT);
      }

      return ContentService.createTextOutput(JSON.stringify({
        success: true,
        message: 'Google ドライブに最新データを保存しました',
        updatedAt: new Date().toISOString(),
        fileUrl: dataFile.getUrl()
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // ----------------------------------------------------
    // B. 請求書写真画像の自動仕分け保存
    // ----------------------------------------------------
    if (action === 'upload_invoice' || data.base64Data) {
      var partner = data.partner || '取引先';
      var dateStr = data.date || Utilities.formatDate(new Date(), 'JST', 'yyyy-MM-dd');
      var base64Data = data.base64Data || '';
      
      var parts = dateStr.split('-');
      var yearMonth = parts[0] + '年' + (parts.length > 1 ? parseInt(parts[1], 10) : '未定') + '月';

      var rootFolder = getOrCreateFolder(DriveApp.getRootFolder(), '請求書');
      var targetFolder = getOrCreateFolder(rootFolder, yearMonth);

      var fileUrl = '';
      var fileName = partner + '_' + dateStr.replace(/[^0-9]/g, '') + '.jpg';
      
      if (base64Data) {
        var contentType = 'image/jpeg';
        var cleanBase64 = base64Data;
        if (base64Data.indexOf(';base64,') !== -1) {
          contentType = base64Data.split(';base64,')[0].replace('data:', '');
          cleanBase64 = base64Data.split(';base64,')[1];
        }
        var decoded = Utilities.base64Decode(cleanBase64);
        var blob = Utilities.newBlob(decoded, contentType, fileName);
        var file = targetFolder.createFile(blob);
        fileUrl = file.getUrl();
      }

      return ContentService.createTextOutput(JSON.stringify({
        success: true,
        fileUrl: fileUrl,
        folderUrl: targetFolder.getUrl(),
        fileName: fileName,
        folderPath: '請求書 / ' + yearMonth
      })).setMimeType(ContentService.MimeType.JSON);
    }

    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      message: '不明なアクション: ' + action
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function getOrCreateFolder(parentFolder, folderName) {
  var folders = parentFolder.getFoldersByName(folderName);
  if (folders.hasNext()) {
    return folders.next();
  } else {
    return parentFolder.createFolder(folderName);
  }
}
