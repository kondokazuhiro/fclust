# GNU GLOBALと自然言語処理ライブラリを利用して、似ている関数を見つける試み

ソースコードタグシステム GNU GLOBAL と python の自然言語処置ライブラリを利用して、
ソースファイル群から、互いにコード内容が似ている関数（メソッド／手続き）を
簡単に抜き出せないかという試みです。

* [出力例](https://kondokazuhiro.github.io/fclust/example/html01/similar.html)

おおまかには以下のような処理手順になっています。

* GNU GLOBAL を利用し、ソースファイル群からタグ情報(definition / reference / symbol)を抽出。
* タグ情報から、definition ごとに reference と symbol を word とした
  BoW(Bag of Words; 識別子の出現頻度) / 特徴ベクトルを作成。
* 特徴ベクトルをクラスタリング（階層型クラスタリング / ウォード法）。
* ベクトル同士の距離が近い definition を選択し、結果をHTMLとして提示。

GNU GLOBAL の definition には、関数定義の他、変数定義、構造体定義、クラス定義
なども含まれますが、reference / symbol の数が一定以上ある definition のみに
絞ることで、概ね関数定義に絞られるようにしています。


## 対応言語

基本的に GNU GLOBAL が対応している言語は概ね対応可能と思われます。
ただし、対象ファイルを取り込む部分で、以下の拡張子のみに制限しています。

* Java (*.java)
* C (*.c)
* C++ (*.cpp, *.cxx, *.cc, *.c++)

拡張子パターン定数(analysis_const.py:TARGET_FNAME_PATTERN)を修正すれば、
他のファイルも取り込めそうですが未確認です。


## 動作OS

Windows, Mac, Linux


## 依存ソフトウェア

* GNU GLOBAL
* Python 3系
* google-code-prettify (本ツールにバンドル)


## 依存 Python ライブラリ

* numpy
* scipy
* sklearn
* jinja2
* matplotlib (optional; dendrogramの生成で使用)
* gensim (doc2vecを使用する場合)

## 依存ソフトウェアのインストール

依存ソフトウェアのインストールについて、一例としてごく簡単に記載します。
インストール方法には様々な選択肢があるため、他の情報も併せて参照してください。

### GNU GLOBAL のインストール

Windows の場合、以下の URL から Windows 32 version をダウンロード・
アーカイブを展開し、環境変数PATHに bin ディレクトリを追加します。

https://www.gnu.org/software/global/download.html

Mac/Linux の場合は、各OSのパッケージシステムからインストール、
またはソースからビルドします。

インストール後、コマンドラインから以下のように実行し、
バージョンが表示されることを確認します(`$`はコマンドラインプロンプト)。

```
$ gtags --version
gtags (GNU GLOBAL) 6.5.6
...略
```


```
$ global --version
global (GNU GLOBAL) 6.5.6
...略
```

### python 3系及び依存ライブラリのインストール

Python 本体に加え上記依存ライブラリが含まれる Anaconda を推奨します。

Windows の場合、以下の URL から Python 3系の Anaconda をダウンロードし、
インストーラを実行します。

https://www.continuum.io/

Mac/Linux の場合は、pyenv 経由で Python 3系 のAnacondaをインストールします。

インストール後、コマンドラインから以下のように実行し、
バージョンが表示されることを確認します(`$`はコマンドラインプロンプト)。

```
$ python --version
Python 3.5.2 :: Anaconda 4.2.0 (64-bit)
```

doc2vec を使用する場合は gensimパッケージをインストールします。

```
$ pip install gensim
```

## 使い方

コマンドラインから以下のように実行します。

**Windows**
```
run.bat src_root result_dir
```
または(doc2vecを使用する場合)
```
run-doc2vec.bat src_root result_dir
```

**Mac / Linux**
```
sh run.sh src_root result_dir
```
または(doc2vecを使用する場合)
```
sh run-doc2vec.sh src_root result_dir
```

* `src_root`は入力対象となるソースファイルが納められたディレクトリです。
  この直下で gtags および global コマンドが実行されます。
* `result_dir`は結果を出力するディレクトリです(gtags コマンドの出力ファイルだけは
  src_root/ 直下に生成されます)。
  result_dir/ 配下には、様々な中間ファイルが生成されますが、最終的なレポートは
  `result_dir/html/similar.html` です。


## 設定項目

各種設定項目は script/analysis_const.py に定数として記述されています。


## 文献メモ

* [情報検索技術に基づく高速な関数クローン検出](https://pdfs.semanticscholar.org/ba9c/317756fb3c0e855277b9e7b6323c840d39d4.pdf)
* [LSHアルゴリズムを利用した類似ソースコードの検索](http://sel.ist.osaka-u.ac.jp/lab-db/betuzuri/archive/1021/1021.pdf)

## License

MIT License
