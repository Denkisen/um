#include "um.h"
#include <QDebug>

Um::Um(const QString db_file_path)
{
    if(QSqlDatabase::isDriverAvailable("QSQLITE"))
    {
        db = QSqlDatabase::addDatabase("QSQLITE");
        db_file = db_file_path;
        db.setDatabaseName(db_file);
    }
}

void Um::OpenDB()
{
    if (!db.isOpen())
    {
        if (!db.open())
        {
            throw std::runtime_error("Open DB Error");
        }
    }
}

void Um::CloseDB()
{
    if (db.isOpen()) db.close();
}

void Um::Clear()
{
    files.clear();
}

void Um::LoadFromDB()
{
    OpenDB();
    tags.clear();
    QSqlQuery query;
    query.prepare("SELECT tags FROM files");
    if (!query.exec())
    {
        QString t = query.lastError().text();
        throw std::runtime_error("Select Query error:");
    }

    while (query.next())
    {
        QStringList list = query.value(0).toString().split(" ");
        list.removeAll("");
        tags.append(list);
    }
    tags.removeDuplicates();
    tags.sort();
    CloseDB();
}

void Um::AddFile(const QString file_path)
{
    OpenDB();
    QStringList all = file_path.split("/");
    QSqlQuery query;
    query.prepare("SELECT tags FROM files WHERE name = ? AND path LIKE ?_");
    query.bindValue(0, all.last());
    all.pop_back();
    query.bindValue(1, all.join("/"));
    if (!query.exec())
        throw std::runtime_error("Select Query error");

    if (query.first())
    {
       files.push_back(UmFile(file_path, query.value(0).toString()));
    }
    else
        throw std::runtime_error("No file in DB");

    CloseDB();
}

void Um::AddDirectory(const QString path)
{
    OpenDB();
    QSqlQuery query;
    query.prepare("SELECT tags, name FROM files WHERE path = ?");
    query.bindValue(0, path);

    if (!query.exec())
        throw std::runtime_error("Select Query error");

    while (query.next())
    {
        QStringList list = query.value(0).toStringList();
        files.push_back(UmFile(path + "/" + list[1], list[0]));
    }

    CloseDB();
}

UmFile& Um::GetFirstFile()
{
    return files.first();
}

UmFile& Um::GetFile(const uint32_t index)
{
    return files[index];
}

void Um::UpdateFile(const uint32_t index)
{
    OpenDB();
    QSqlQuery query;
    query.prepare("UPDATE files SET tags = ? WHERE name = ?");
    query.bindValue(0, files[index].GetTags().join(" "));
    query.bindValue(1, files[index].GetFile().split("/").last());

    if (!query.exec())
        throw std::runtime_error("Select Query error");
    CloseDB();
}

QStringList Um::Suggest(const QString s)
{
    QStringList result;
    for (auto &t : tags)
    {
        if (t.contains(s))
            result.push_back(t);
    }
    return result;
}

int32_t Um::IndexOfTag(QString t)
{
    return tags.indexOf(t);
}

void Um::RemoveFile(const uint32_t index)
{
    files.removeAt(index);
}

Um::~Um()
{
    CloseDB();
}
