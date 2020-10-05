#ifndef UM_H
#define UM_H

#include <QString>
#include <QStringList>
#include <QtSql>
#include <QSqlDatabase>
#include <QSqlDriver>
#include <QSqlError>
#include <QSqlQuery>
#include <QVector>
#include <QVariant>

#include "umfile.h"

class Um
{
private:
    QSqlDatabase db;
    QString db_file = "";
    QVector<UmFile> files;
    QStringList tags;
public:
    Um() = delete;
    Um(const Um &obj) = delete;
    Um& operator=(const Um &obj) = delete;
    Um(const QString db_file_path);
    void OpenDB();
    void CloseDB();
    void Clear();
    void AddFile(const QString file_path);
    void AddDirectory(const QString path);
    uint32_t FilesCount() { return files.size(); }
    void LoadFromDB();
    UmFile& GetFirstFile();
    UmFile& GetFile(const uint32_t index);
    void UpdateFile(const uint32_t index);
    void RemoveFile(const uint32_t index);
    bool IsOpen() { return db.isOpen(); }
    QString GetLastDBError() { return db.lastError().text(); }
    QStringList GetAllTags() { return tags; }
    QStringList Suggest(const QString s);
    int32_t IndexOfTag(QString t);

    ~Um();
};

#endif // UM_H
