---
title: "ChatGPT + textlint + reviewdog で最高の文章を無限に生成しよう"
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["ChatGPT", "CI", "reviewdog"]
published: true
published_at: 2023-04-17 09:00
---

## tl;dr

人間の生成する文章はカス^[過激]なので，CI で textlint と chatgpt に推敲してもらい，最高の文章を生成しよう！！

## はじめに

### 対象読者

以下のような人を対象として書いています．

- 自分の書いた文章に自信がない
- 文章の推敲をしたいが，本質的でない部分の指摘に人的リソースを割きたくない
- 全てのものをCIによって自動化したい^[個人的には本当に全てのものを自動化し，人間はお昼寝をしていれば良い世界が来てほしい]

### なにをやるの？？

プルリク駆動で書き上げる任意の文章に対して，**自動的に**

1. 勝手に文法ミスを指摘してもらい，
2. さらにChatGPTにより全体のレビューをしてもらえる

世界を作ります．（実際に文法ミスを指摘されているの図）

![自動的にレビューしているの図](/images/auto-review.png)

ただし，あくまでもレビューコメントとして表示されるだけで，CI GREEN は担保していることにします^[「"に"が2回以上使われているのでマージできません！！」はストレスがある]．

## 使う技術

### textlint

[textlint](https://textlint.github.io) は自然言語向けのlinterです．ESLint を既に知っている場合は，その自然言語版と考えてくもらうとわかりやすいかもしれません．`.txt` はもちろんのこと，プラグインを用いることで `.md` や `.tex` にも対応できるそうです^[便利]．textlint の特徴的な機能として，**デフォルトではルールが存在しない** という点があります．これは，自然言語には多くのルールが存在するため，デフォルトでルールを提供するのではなく，ユーザが自由にルールを設定できるようにしているためだそうです．

それゆえに textlint を使うには，**ルールを設定する必要があります**．今回は，[textlint-rule-preset-japanese](https://github.com/textlint-ja/textlint-rule-preset-japanese) というpresetを利用してみます．これは日本語の文章全般に対して適用できるルールのpresetです．これは例えば

- 句点を一文の中でn回以上使用している
- 一文の長さがn文字以上
- 二重否定
- 二重動詞
- 制御文字

などを検出，指摘してくれます．便利ですね．

類似のpresetとして，[textlint-rule-preset-ja-technical-writing](https://github.com/textlint-ja/textlint-rule-preset-ja-technical-writing) という技術文書向けのpresetも用意されているので，適宜導入すると面白いと思います．

### reviewdog

みなさん大好き [reviewdog](https://github.com/reviewdog/reviewdog) です．reviewdog は，CIで実行されたlinterの結果をGitHub（やその他の任意のコードホスティングサービス）のPRにコメントするためのツールです．アイコンのわんちゃん🐶がかわいくて大変良いですね．

今回は，textlint の出力を reviewdog に渡して，プルリクにコメントするようにします．reviewdog は，[Reviewdog Diagnostic Format](https://github.com/reviewdog/reviewdog/tree/master/proto/rdf) (RDFormat) という独自のフォーマットを使うことで任意のlint^[スキーマさえ満たしていればlintである必要すらない．なおそれに需要があるのかは不明]の結果を受け取れます．textlint の出力は，このRDFormatに対応していない^[2023/04/16 現在メンテナンスされている変換ツールが存在しない]ため，textlintの出力をRDFormatに変換する必要があります．

### ChatGPT

散々話題になっているので，「この記事で初めて知った！！」という人はいないと思います．ChatGPTとは何かChatGPTに聞いてみたところ，

> ChatGPTは、OpenAIが開発した大規模な言語モデルの1つです。GPT（Generative Pretrained Transformer）の3.5バージョンに基づいており、自然言語処理の分野で広く使用されています。ChatGPTは、人間のように応答し、自然な会話を行うことができるため、様々なタスクで利用されます。例えば、質問応答、翻訳、文章生成、文章要約などがあります

とのことでした．

当然，人間の書いた文章（もといソースコード）に対して対話的にレビューを行うこともできます．既にそのようなActionsは公開されているので，今回はそれを使うことにします．

https://github.com/anc95/ChatGPT-CodeReview

## 作り方

### textlint + reviewdog

各々のワークフローファイルを定義していきます．textlint + reviewdog のCIの構築に関しては，既にいくつかの参考記事^[参考資料の項目]があるので，合わせて読んでみてください．既存のワークフローでいい感じに動作するものがなかったので，今回はサクッと作ってみました．

textlint の結果を，reviedog が読み込める形式に変換するスクリプトを作り^[Nodeで書けという話がありますが，PythonのがMVP(Minimum Viable Product)が作りやすかったので許してください．リファクタリングのコントリビューションをお待ちしています]...

https://github.com/Okabe-Junya/zenn-docs-public/blob/main/.github/script/convert.py

実際に textlint の結果を変換スクリプトに送り込み...

```bash
npx textlint "**/*.md" --format json | python .github/script/convert.py >./report.json
```

変換スクリプトの出力を reviewdog に渡すようにします．

```bash
if [ -s ./report.json ]; then
    cat ./report.json | reviewdog -f=rdjson -reporter=github-pr-review
else
    echo "No errors found"
fi
```

あとはこれをワークフロー化して，GitHub Actions に登録するだけです．実際の実装は

https://github.com/Okabe-Junya/zenn-docs-public

の `.github/` においてあります^[使いやすいように早急にマーケットプレイスに登録しろという話がある]．

### Chatgpt Code Review

[anc95/ChatGPT-CodeReview](https://github.com/anc95/ChatGPT-CodeReview) に懇切丁寧な説明が書かれているので，特筆すべきことはないですが，以下のようなワークフローを定義することで，ChatGPTによるレビューを実現できます．

```yaml
name: Code Review

permissions:
  contents: read
  pull-requests: write

on:
  pull_request:
    branches:
      - main

jobs:
  chatgpt-review:
    runs-on: ubuntu-latest
    steps:
      - uses: anc95/ChatGPT-CodeReview@main
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        timeout-minutes: 5
```

注意すべき点としては，

1. ChatGPTのAPIキーをGitHubのSecretsに登録する必要がある （参考: [README#Configuration](https://github.com/anc95/ChatGPT-CodeReview#configuration)）
2. Publicリポジトリで実装すると，勝手にガンガンCIを回されて，とんでも請求が来る可能性がある^[ので [Okabe-Junya/zenn-docs-public](https://github.com/Okabe-Junya/zenn-docs-public) にもこのワークフローはおいていない]

があげられます．特に2つ目はマジでお気をつけください．

## 結果

はい

![自動的にレビューしているの図](/images/auto-review.png)
![自動的にレビューしているの図2](/images/auto-review2.png)

ChatGPTのレビューが日本語化対応されていないのが悔やまれますが，いい感じにレビューしてくれています^[コントリビュートしようという機運があるので，時間を見つけてやりたい]．当然，指摘された事項を修正するもしないも自由です．人的リソースを一切使っていないので，リジェクトへの心理的負担が非常に小さいのも高評価ですね．

## まとめ

自動レビューを生成することで，「僕の考える最強の世界」に一歩近づいた気がします．

**プログラムによるレビューを行った後にようやく人間がレビューを行う** というのは，貴重な人間の時間を節約することができます．また，「些細なことですが」のようなプレフィックスから始まる本質的でない箇所のレビューを減らすこともできます．

近頃は DevOps や SRE, CI/CD などの言葉を耳にする機会が多く，ソースコード/ソフトウェアの品質を担保するためのツールや手法が数多く存在しています．決定的なルールが少ないことやVCSで管理しないなどの背景ゆえ，自然言語に対してこれらが導入されることはあまりないように思いますが，ChatGPTの登場を皮切りに大きな変革が起こることを楽しみにしています．そしてこの記事がその一端を担えるともっと嬉しいなぁと思っています．

## 参考資料

- [GitHub ActionsでZennブログの校正を自動化してみた](https://zenn.dev/yuta28/articles/blog-lint-ci-reviewdog)
- [zenn-cli + reviewdog + textlint + GitHub Actions で執筆体験を最高にする](https://zenn.dev/serima/articles/4dac7baf0b9377b0b58b)
- [azu/textlint-reviewdog-example](https://github.com/azu/textlint-reviewdog-example)
