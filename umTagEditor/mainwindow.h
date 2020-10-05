#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QListWidgetItem>
#include <map>
#include <memory>

#include "um.h"
#include "umfile.h"

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

protected:
    void showEvent(QShowEvent *ev);
    void resizeEvent(QResizeEvent*);
    bool eventFilter(QObject *obj, QEvent *event);

private slots:
    void on_actionOpen_DB_triggered();

    void on_actionOpen_File_triggered();

    void on_kiconbutton_clicked();

    void on_searchComboBox_activated(const QString &arg1);

    void on_SavePushButton_clicked();

    void on_selectedTagsListWidget_itemChanged(QListWidgetItem *item);

    void on_actionOpen_Directory_triggered();

    void on_NextPushButton_clicked();

    void on_BackPushButton_clicked();

    void on_filesListWidget_itemClicked(QListWidgetItem *item);

private:
    Ui::MainWindow *ui;
    std::unique_ptr<Um> db;
    size_t current_file = 0;

    void OnShowEvent();
    void ChangeFile(size_t index);
    QPixmap OpenImage(QString file_name, uint32_t w, uint32_t h);
};
#endif // MAINWINDOW_H
