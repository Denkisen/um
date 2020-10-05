#ifndef UMFILE_H
#define UMFILE_H

#include <QString>
#include <QStringList>

class UmFile
{
private:
    QString path = "";
    QStringList tag_list;
public:
    UmFile() = default;
    UmFile(UmFile &&obj) = default;
    UmFile(const UmFile &obj) = default;
    UmFile& operator= (const UmFile &obj) = default;
    ~UmFile() = default;
    UmFile(const QString file_path) : path(file_path) {};
    UmFile(const QString file_path, const QString tags) : path(file_path), tag_list(tags.split(" ")) { tag_list.removeDuplicates(); };
    UmFile(const QString file_path, const QStringList tags) : path(file_path), tag_list(tags) { tag_list.removeDuplicates(); };
    void SetFile(const QString path);
    void SetTags(const QString tags);
    void SetTags(const QStringList tags);
    void AddTag(const QString tag);
    void DelTag(const QString tag);
    QStringList GetTags() { return tag_list; }
    QString GetFile() { return path; }
};

#endif // UMFILE_H
