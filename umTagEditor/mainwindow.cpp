#include "mainwindow.h"
#include "ui_mainwindow.h"
#include <QPicture>
#include <QFileDialog>
#include <QErrorMessage>
#include <QKeyEvent>
#include <QListView>
#include <QTreeView>
#include <QtMath>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    ui->filesListWidget->installEventFilter(this);
}

void MainWindow::showEvent(QShowEvent *ev)
{
    QMainWindow::showEvent(ev);
    OnShowEvent();
}

void MainWindow::OnShowEvent()
{

}

void MainWindow::resizeEvent(QResizeEvent* event)
{
   QMainWindow::resizeEvent(event);
   if (db.get() != nullptr && db->FilesCount() > 0)
   {
       auto w = ui->labelGridWidget->width();
       auto h = ui->labelGridWidget->height();
       QPixmap item = OpenImage(db->GetFile(current_file).GetFile(), w, h);
       ui->imageLabel->setPixmap(item);
   }
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_actionOpen_DB_triggered()
{
    QFileDialog open_db(this);
    open_db.setFileMode(QFileDialog::FileMode::ExistingFile);
    open_db.setViewMode(QFileDialog::Detail);
    open_db.setOption(QFileDialog::DontUseNativeDialog, true);
    if (open_db.exec())
        db = std::make_unique<Um>(open_db.selectedFiles().first());
    if (db.get() != nullptr)
    {
        db->LoadFromDB();
    }
}

void MainWindow::ChangeFile(size_t index)
{
    if (db->FilesCount() == 0)
        return;
    if (index >= db->FilesCount())
        current_file = 0;
    else
        current_file = index;

    ui->filesListWidget->setCurrentRow(current_file);

    ui->selectedTagsListWidget->clear();
    for (auto &s : db->GetFile(current_file).GetTags())
    {
        QListWidgetItem *item = new QListWidgetItem();
        item->setCheckState(Qt::CheckState::Checked);
        item->setText(s);
        item->setHidden(false);
        item->setFlags(Qt::ItemIsEnabled | Qt::ItemIsUserCheckable );
        ui->selectedTagsListWidget->addItem(item);
    }

    auto w = ui->labelGridWidget->width();
    auto h = ui->labelGridWidget->height();
    QPixmap item = OpenImage(db->GetFile(current_file).GetFile(), w, h);
    ui->imageLabel->setPixmap(item);
}

void MainWindow::on_actionOpen_File_triggered()
{
    QFileDialog open_db(this);
    open_db.setFileMode(QFileDialog::FileMode::ExistingFiles);
    open_db.setViewMode(QFileDialog::Detail);
    open_db.setOption(QFileDialog::DontUseNativeDialog, true);
    open_db.setNameFilter(tr("Images (*.png *.bmp *.jpg *.jpeg)"));

    if (open_db.exec() && db.get() != nullptr)
    {
        auto files = open_db.selectedFiles();
        for (auto &f : files) db->AddFile(f);
        ui->filesListWidget->addItems(files);
        if (db->FilesCount() > 0)
            ChangeFile(db->FilesCount() - files.count());
    }
}

void MainWindow::on_kiconbutton_clicked()
{
 QString s = ui->searchComboBox->currentText();
 ui->searchComboBox->clear();
 ui->searchComboBox->insertItems(0, db->Suggest(s));
}

void MainWindow::on_searchComboBox_activated(const QString &arg1)
{
    auto items = ui->selectedTagsListWidget->findItems(arg1, Qt::MatchFlag::MatchContains | Qt::MatchFlag::MatchExactly);
    if (items.empty())
    {
        QListWidgetItem *item = new QListWidgetItem();
        item->setCheckState(Qt::CheckState::Unchecked);
        item->setText(arg1);
        item->setHidden(false);
        item->setFlags(Qt::ItemIsEnabled | Qt::ItemIsUserCheckable );

        ui->selectedTagsListWidget->addItem(item);
    }
}

void MainWindow::on_SavePushButton_clicked()
{
    db->UpdateFile(current_file);
}

void MainWindow::on_selectedTagsListWidget_itemChanged(QListWidgetItem *item)
{
    if (item->checkState() == Qt::Checked)
        db->GetFile(current_file).AddTag(item->text());
    else if (item->checkState() == Qt::Unchecked)
        db->GetFile(current_file).DelTag(item->text());
}

void MainWindow::on_actionOpen_Directory_triggered()
{
    QFileDialog open_db(this);
    open_db.setFileMode(QFileDialog::FileMode::Directory);
    open_db.setViewMode(QFileDialog::Detail);
    open_db.setOption(QFileDialog::DontUseNativeDialog, true);
    QListView *l = open_db.findChild<QListView*>("listView");
    if (l)
    {
         l->setSelectionMode(QAbstractItemView::MultiSelection);
    }
    QTreeView *t = open_db.findChild<QTreeView*>();
    if (t)
    {
       t->setSelectionMode(QAbstractItemView::MultiSelection);
    }

    if (open_db.exec() && db.get() != nullptr)
    {
        auto dirs = open_db.selectedFiles();
        QStringList files;
        for (auto &d : dirs)
        {
           QDir directory(d);
           auto tmp = directory.entryList(QStringList() << "*.jpg" << "*.JPG" << "*.png" << "*.PNG" << "*.bmp" << "*.BMP" << "*.jpeg" << "*.JPEG", QDir::Files);
           for (auto &t: tmp) t = d + "/" + t;
           files.append(tmp);
        }

        for (auto &f : files) db->AddFile(f);
        ui->filesListWidget->addItems(files);
        if (db->FilesCount() > 0)
            ChangeFile(db->FilesCount() - files.count());
    }
}

void MainWindow::on_NextPushButton_clicked()
{
    size_t tmp = current_file + 1;
    ChangeFile(tmp >= db->FilesCount() ? 0 : tmp);
}

void MainWindow::on_BackPushButton_clicked()
{
    int tmp = current_file - 1;
    ChangeFile(tmp < 0 ? db->FilesCount() - 1 : tmp);
}

void MainWindow::on_filesListWidget_itemClicked(QListWidgetItem *item)
{
    auto index = ui->filesListWidget->currentRow();
    ChangeFile(index);
}

bool MainWindow::eventFilter(QObject *obj, QEvent *event)
{
    if (event->type() == QEvent::KeyRelease)
    {
        QKeyEvent *keyEvent = static_cast<QKeyEvent *>(event);
        if (obj == ui->filesListWidget)
        {
            if (keyEvent->key() == Qt::Key_Delete)
            {
                if (db->FilesCount() > 0)
                {
                    auto row = ui->filesListWidget->row(ui->filesListWidget->selectedItems().first());
                    db->RemoveFile(row);
                    ui->filesListWidget->model()->removeRow(row);
                    if (db->FilesCount() > 0)
                    {
                        on_NextPushButton_clicked();
                    }
                }
            }
        }
    }
    return true;
}

QPixmap MainWindow::OpenImage(QString file_name, uint32_t w, uint32_t h)
{
    cv::Mat image = cv::imread(file_name.toStdString().c_str());
    cv::Mat res;
    float rate = qMin(w / (float) image.cols, h / (float) image.rows);
    cv::Size s(image.cols * rate, image.rows * rate);
    cv::resize(image, res, s, 0.0, 0.0, rate > 1.0 ? cv::INTER_LINEAR : cv::INTER_AREA);
    image = res;
    QImage img(image.data, image.cols, image.rows, static_cast<int>(image.step), QImage::Format_RGB888);
    return QPixmap::fromImage(img.rgbSwapped());
}
