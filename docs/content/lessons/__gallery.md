## cards

```figure
{
 "type": "cards",
 "cols": 3,
 "title": "勘が信頼できる3条件",
 "caption": "1つでも欠けると、経験則は静かに外れ始める",
 "items": [
  {
   "icon": "🔁",
   "title": "繰り返しがある",
   "text": "同じような状況を何十回も経験している。初めての事業や新商品では成立しない。",
   "tone": "blue"
  },
  {
   "icon": "⏱",
   "title": "フィードバックが速い",
   "text": "判断の結果が数日以内にわかる。1年後にしか結果が出ない判断では、経験は蓄積されない。",
   "tone": "green"
  },
  {
   "icon": "🌏",
   "title": "環境が安定している",
   "text": "ルールが変わらない。市場や顧客層が急変すると、過去の経験がそのまま誤りになる。",
   "tone": "amber"
  }
 ]
}
```

## chart

```figure
{
 "type": "chart",
 "kind": "bar",
 "title": "カテゴリ別売上金額（2024-2025年 合計）",
 "caption": "金額で見ると家電が圧倒的。ただし「数量で見ると」答えは変わる",
 "categories": [
  "家電",
  "衣料",
  "食品"
 ],
 "series": [
  {
   "name": "売上金額",
   "values": [
    234.5,
    34.7,
    6.8
   ],
   "tone": "blue"
  }
 ],
 "highlight": 0,
 "unit": "百万円"
}
```

## compare

```figure
{
 "type": "compare",
 "title": "同じ売上データ、2つの読み方",
 "caption": "印象は強いほうに引っ張られる。だから記録が要る",
 "panels": [
  {
   "title": "印象で語る",
   "tone": "bad",
   "items": [
    "「最近、家電が売れてない気がする」",
    "根拠は直近1週間の店頭の体感",
    "反論できないので声が大きい人の意見が通る",
    "翌月には誰も何を決めたか覚えていない"
   ],
   "note": "再現できない"
  },
  {
   "title": "データで語る",
   "tone": "good",
   "items": [
    "「家電カテゴリは2年間で売上の85%を占める」",
    "根拠は6,948件の全注文明細",
    "定義と集計方法が示されるので検証できる",
    "同じ集計を来月も自動で再現できる"
   ],
   "note": "再現できる"
  }
 ]
}
```

## flow

```figure
{
 "type": "flow",
 "dir": "row",
 "title": "データが人間を補う4つの機能",
 "caption": "どれか1つでも欠けると、意思決定は勘に戻る",
 "items": [
  {
   "label": "記憶",
   "sub": "3年前の同じ月を\n正確に思い出す",
   "tone": "blue",
   "icon": "🧠"
  },
  {
   "label": "網羅",
   "sub": "6,948件を\n1件も漏らさず数える",
   "tone": "green",
   "icon": "🔍"
  },
  {
   "label": "比較",
   "sub": "前年・他店舗・目標と\n同じ基準で並べる",
   "tone": "amber",
   "icon": "⚖"
  },
  {
   "label": "共有",
   "sub": "全員が同じ数字を\n同じ定義で見る",
   "tone": "violet",
   "icon": "🤝"
  }
 ]
}
```

## formula

```figure
{
 "type": "formula",
 "lang": "text",
 "code": "売上 = 客数 × 客単価 = ( 来店数 × 購買率 ) × ( 商品単価 × 買上点数 )",
 "parts": [
  {
   "match": "来店数",
   "label": "販促・立地。先行指標として日次で見る",
   "tone": "blue"
  },
  {
   "match": "購買率",
   "label": "接客と在庫の質。欠品があると即落ちる",
   "tone": "green"
  },
  {
   "match": "商品単価",
   "label": "値引き施策の影響が最も出る箇所",
   "tone": "amber"
  },
  {
   "match": "買上点数",
   "label": "売場配置とクロスセルで動かす",
   "tone": "violet"
  }
 ]
}
```

## interactive

```figure
{
 "type": "interactive",
 "widget": "visual-picker",
 "title": "何を知りたいかからビジュアルを選ぶ",
 "caption": "問いを選ぶと、対応するビジュアルと注意点が表示される"
}
```

## matrix

```figure
{
 "type": "matrix",
 "title": "勘とデータの使い分け",
 "caption": "右上に近いほどデータの投資対効果が高い。左下は会議で議論するだけ無駄な領域",
 "xLabel": "判断の頻度・繰り返し",
 "yLabel": "環境の変化の速さ",
 "xLow": "1回きり",
 "xHigh": "毎日繰り返す",
 "yLow": "安定",
 "yHigh": "激しい",
 "quadrants": [
  {
   "title": "仮説と小さな実験",
   "text": "データが足りない領域。まず測る仕組みを作る。",
   "tone": "amber"
  },
  {
   "title": "データが必須",
   "text": "日次の在庫・広告配分・価格。人間の勘では追随できない。",
   "tone": "good"
  },
  {
   "title": "経験と判断で十分",
   "text": "社名の決定、オフィス移転。何度も繰り返さない判断。",
   "tone": "gray"
  },
  {
   "title": "自動化の対象",
   "text": "ルールが安定し繰り返しも多い。ダッシュボード化して定型化する。",
   "tone": "blue"
  }
 ]
}
```

## pipeline

```figure
{
 "type": "pipeline",
 "title": "分析が組織に定着する回路",
 "caption": "点線の戻り矢印が切れている組織では、レポートは飾りになる",
 "nodes": [
  {
   "id": "q",
   "label": "問い",
   "tone": "blue"
  },
  {
   "id": "d",
   "label": "データ",
   "tone": "green"
  },
  {
   "id": "v",
   "label": "可視化",
   "tone": "amber"
  },
  {
   "id": "a",
   "label": "行動",
   "tone": "violet"
  },
  {
   "id": "r",
   "label": "結果の測定",
   "tone": "pink"
  }
 ],
 "edges": [
  {
   "from": "q",
   "to": "d",
   "label": "必要な範囲を決める"
  },
  {
   "from": "d",
   "to": "v",
   "label": "読める形にする"
  },
  {
   "from": "v",
   "to": "a",
   "label": "判断する"
  },
  {
   "from": "a",
   "to": "r",
   "label": "効果を測る"
  },
  {
   "from": "r",
   "to": "q",
   "label": "次の問いが生まれる"
  }
 ]
}
```

## stack

```figure
{
 "type": "stack",
 "title": "分析の4段階",
 "caption": "上に行くほど価値は高いが、下の段が固まっていないと上は砂上の楼閣になる",
 "layers": [
  {
   "label": "処方的分析 Prescriptive",
   "sub": "どうすべきか — 在庫を何個発注すべきか",
   "tone": "pink"
  },
  {
   "label": "予測的分析 Predictive",
   "sub": "何が起きそうか — 来月の需要はいくつか",
   "tone": "violet"
  },
  {
   "label": "診断的分析 Diagnostic",
   "sub": "なぜ起きたか — どの店舗のどの商品が落ちたか",
   "tone": "amber"
  },
  {
   "label": "記述的分析 Descriptive",
   "sub": "何が起きたか — 先月の売上は1,875万円だった",
   "tone": "blue"
  }
 ]
}
```

## star

```figure
{
 "type": "star",
 "title": "モデル化のゴール — スタースキーマ",
 "caption": "中心に数値（ファクト）、周りに切り口（ディメンション）。ティア2で本格的に扱う",
 "fact": {
  "label": "売上（Fact）",
  "lines": [
   "OrderDate / ProductID / StoreID",
   "Quantity / SalesAmount"
  ]
 },
 "dims": [
  {
   "label": "商品（Dim）",
   "lines": [
    "ProductName / Category"
   ]
  },
  {
   "label": "店舗（Dim）",
   "lines": [
    "StoreName / Region"
   ]
  },
  {
   "label": "顧客（Dim）",
   "lines": [
    "Segment / Prefecture"
   ]
  },
  {
   "label": "日付（Dim）",
   "lines": [
    "年 / 四半期 / 月"
   ]
  }
 ],
 "edgeLabel": "1対多"
}
```

## steps

```figure
{
 "type": "steps",
 "title": "分析サイクルの6ステップ",
 "caption": "1と6を飛ばした分析は、必ず「きれいなグラフ」で終わる",
 "items": [
  {
   "title": "1. 問いを立てる",
   "text": "「今月の販促予算を、どの店舗に配分すべきか」のように、判断につながる形にする。「売上を見たい」は問いではない。",
   "tone": "blue"
  },
  {
   "title": "2. 指標を決める",
   "text": "その問いに答えるための数字を定義する。分子・分母・期間・除外条件まで書く。L0103で詳しく扱う。",
   "tone": "blue"
  },
  {
   "title": "3. データを集めて整える",
   "text": "必要な粒度でデータを取得し、型を整え、欠損や異常値を確認する。M03・M04の範囲。",
   "tone": "green"
  },
  {
   "title": "4. 可視化して読む",
   "text": "比較・推移・構成・分布・関係のどれかの型でグラフにする。L0105で扱う。",
   "tone": "amber"
  },
  {
   "title": "5. 解釈して仮説を作る",
   "text": "「なぜそうなったか」を推測する。ここは人間の仕事であり、業務知識が効く。",
   "tone": "violet"
  },
  {
   "title": "6. 行動して結果を測る",
   "text": "施策を打ち、効果を同じ指標で測る。測らなければ、次回も同じ勘に戻る。",
   "tone": "pink"
  }
 ]
}
```

## tablediff

```figure
{
 "type": "tablediff",
 "arrowLabel": "月×店舗で集約（不可逆）",
 "before": {
  "title": "明細粒度（元データ）",
  "tone": "good",
  "head": [
   "OrderID",
   "OrderDate",
   "StoreID",
   "ProductID",
   "SalesAmount"
  ],
  "rows": [
   [
    "O000001",
    "2024-01-01",
    "S005",
    "P0027",
    "1580"
   ],
   [
    "O000002",
    "2024-01-01",
    "S008",
    "P0011",
    "6980"
   ],
   [
    "O000003",
    "2024-01-02",
    "S005",
    "P0002",
    "238000"
   ]
  ]
 },
 "after": {
  "title": "月次集約（軽いが情報は失われた）",
  "tone": "amber",
  "head": [
   "年月",
   "StoreID",
   "売上合計"
  ],
  "rows": [
   [
    "2024-01",
    "S005",
    "!239580"
   ],
   [
    "2024-01",
    "S008",
    "6980"
   ]
  ]
 }
}
```

## timeline

```figure
{
 "type": "timeline",
 "title": "M01の流れ",
 "caption": "道具を持つ前に、何を測るかを決める",
 "items": [
  {
   "label": "L0101",
   "title": "なぜ分析するのか",
   "text": "勘の限界と、データが補う範囲を知る",
   "tone": "blue"
  },
  {
   "label": "L0102",
   "title": "データの階段",
   "text": "データを意思決定まで運ぶ4段を知る",
   "tone": "green"
  },
  {
   "label": "L0103",
   "title": "KPI設計",
   "text": "何を測るかで組織の行動が変わる",
   "tone": "amber"
  },
  {
   "label": "L0104",
   "title": "数字の読み方",
   "text": "平均のウソを見抜き分布で語る",
   "tone": "violet"
  },
  {
   "label": "L0105",
   "title": "分析の5つの型",
   "text": "問いをグラフに翻訳する技術",
   "tone": "pink"
  }
 ]
}
```

## tree

```figure
{
 "type": "tree",
 "title": "レポートが使われなくなる原因",
 "caption": "原因の8割は「作る前」の設計にある",
 "root": {
  "label": "誰も見ないレポート"
 },
 "children": [
  {
   "label": "問いがない",
   "sub": "何を判断するために作ったか不明",
   "tone": "bad",
   "children": [
    {
     "label": "依頼が「売上を可視化して」だけ"
    },
    {
     "label": "見た人が次の行動を思いつかない"
    }
   ]
  },
  {
   "label": "信頼されていない",
   "sub": "数字が他の資料と合わない",
   "tone": "bad",
   "children": [
    {
     "label": "定義が書かれていない"
    },
    {
     "label": "更新が止まっている"
    }
   ]
  },
  {
   "label": "読むのに時間がかかる",
   "sub": "1画面に20個のグラフ",
   "tone": "amber",
   "children": [
    {
     "label": "重要な数字がどれか分からない"
    }
   ]
  }
 ]
}
```
