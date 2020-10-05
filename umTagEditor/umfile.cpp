#include "umfile.h"

void UmFile::SetFile(const QString path)
{
    this->path = path;
}

void UmFile::SetTags(const QString tags)
{
    tag_list = tags.split(" ");
    tag_list.removeDuplicates();
}

void UmFile::SetTags(const QStringList tags)
{
    tag_list = tags;
    tag_list.removeDuplicates();
}

void UmFile::AddTag(const QString tag)
{
    tag_list.push_back(tag);
    tag_list.removeDuplicates();
}

void UmFile::DelTag(const QString tag)
{
    tag_list.removeOne(tag);
}
