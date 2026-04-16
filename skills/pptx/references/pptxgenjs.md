# PptxGenJS リファレンス

Node.js で PowerPoint ファイルを生成するための PptxGenJS の使い方ガイド。

## セットアップ

```javascript
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10" x 5.625"
pres.author = "Author Name";
pres.title = "Presentation Title";

let slide = pres.addSlide();
slide.addText("Hello World!", { x: 0.5, y: 0.5, fontSize: 36, color: "363636" });

pres.writeFile({ fileName: "output.pptx" });
```

## レイアウトサイズ

| レイアウト | 幅 x 高さ |
|-----------|-----------|
| `LAYOUT_16x9` | 10" x 5.625"（デフォルト） |
| `LAYOUT_16x10` | 10" x 6.25" |
| `LAYOUT_4x3` | 10" x 7.5" |
| `LAYOUT_WIDE` | 13.3" x 7.5" |

---

## テキスト

```javascript
// 基本テキスト
slide.addText("Simple Text", {
  x: 1, y: 1, w: 8, h: 2,
  fontSize: 24, fontFace: "Arial",
  color: "363636", bold: true,
  align: "center", valign: "middle"
});

// リッチテキスト（複数スタイル混在）
slide.addText([
  { text: "太字 ", options: { bold: true } },
  { text: "イタリック ", options: { italic: true } },
  { text: "通常" }
], { x: 1, y: 3, w: 8, h: 1 });

// 複数行テキスト（breakLine: true が必要）
slide.addText([
  { text: "1行目", options: { breakLine: true } },
  { text: "2行目", options: { breakLine: true } },
  { text: "3行目" }
], { x: 0.5, y: 0.5, w: 8, h: 2 });

// テキストボックスのマージン
// 他の要素と位置合わせするときは margin: 0 にする
slide.addText("Title", {
  x: 0.5, y: 0.3, w: 9, h: 0.6,
  margin: 0
});

// 文字間隔（charSpacing を使う。letterSpacing は無視される）
slide.addText("SPACED TEXT", { x: 1, y: 1, w: 8, h: 1, charSpacing: 6 });
```

---

## 箇条書き

```javascript
// ✅ 正しい書き方
slide.addText([
  { text: "項目1", options: { bullet: true, breakLine: true } },
  { text: "項目2", options: { bullet: true, breakLine: true } },
  { text: "項目3", options: { bullet: true } }
], { x: 0.5, y: 0.5, w: 8, h: 3 });

// ❌ 間違い: Unicode の箇条書き記号を使わない（二重になる）
slide.addText("• 項目1", { ... });

// サブ項目
{ text: "サブ項目", options: { bullet: true, indentLevel: 1 } }

// 番号付きリスト
{ text: "最初", options: { bullet: { type: "number" }, breakLine: true } }
```

**注意:** `lineSpacing` と箇条書きを併用すると過剰な間隔になる。`paraSpaceAfter` を使うこと。

---

## 図形

```javascript
// 四角形
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.8, w: 1.5, h: 3.0,
  fill: { color: "FF0000" },
  line: { color: "000000", width: 2 }
});

// 円
slide.addShape(pres.shapes.OVAL, {
  x: 4, y: 1, w: 2, h: 2,
  fill: { color: "0000FF" }
});

// 線
slide.addShape(pres.shapes.LINE, {
  x: 1, y: 3, w: 5, h: 0,
  line: { color: "FF0000", width: 3, dashType: "dash" }
});

// 透過
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "0088CC", transparency: 50 }
});

// 角丸四角形
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "FFFFFF" },
  rectRadius: 0.1
});

// 影
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "FFFFFF" },
  shadow: {
    type: "outer", color: "000000",
    blur: 6, offset: 2, angle: 135, opacity: 0.15
  }
});
```

### 影のプロパティ

| プロパティ | 型 | 範囲 | 備考 |
|-----------|-----|------|------|
| `type` | string | `"outer"`, `"inner"` | |
| `color` | string | 6桁hex（例: `"000000"`） | `#` 不要、8桁hex 禁止 |
| `blur` | number | 0-100 pt | |
| `offset` | number | 0-200 pt | **負の値禁止**（ファイル破損） |
| `angle` | number | 0-359 度 | 135=右下、270=上方向 |
| `opacity` | number | 0.0-1.0 | 透明度はここで指定 |

---

## 背景

```javascript
// 単色
slide.background = { color: "F1F1F1" };

// 画像（URL）
slide.background = { path: "https://example.com/bg.jpg" };

// 画像（Base64）
slide.background = { data: "image/png;base64,iVBORw0KGgo..." };
```

---

## テーブル

```javascript
slide.addTable([
  ["ヘッダー1", "ヘッダー2"],
  ["セル1", "セル2"]
], {
  x: 1, y: 1, w: 8, h: 2,
  border: { pt: 1, color: "999999" },
  fill: { color: "F1F1F1" }
});

// スタイル付き
let tableData = [
  [
    { text: "ヘッダー", options: { fill: { color: "6699CC" }, color: "FFFFFF", bold: true } },
    "セル"
  ],
  [{ text: "結合セル", options: { colspan: 2 } }]
];
slide.addTable(tableData, { x: 1, y: 3.5, w: 8, colW: [4, 4] });
```

---

## チャート

```javascript
// 棒グラフ
slide.addChart(pres.charts.BAR, [{
  name: "売上", labels: ["Q1", "Q2", "Q3", "Q4"],
  values: [4500, 5500, 6200, 7100]
}], {
  x: 0.5, y: 0.6, w: 6, h: 3,
  barDir: "col",
  showTitle: true, title: "四半期別売上"
});

// 折れ線グラフ
slide.addChart(pres.charts.LINE, [{
  name: "温度", labels: ["1月", "2月", "3月"],
  values: [5, 8, 14]
}], {
  x: 0.5, y: 4, w: 6, h: 3,
  lineSize: 3, lineSmooth: true
});

// 円グラフ
slide.addChart(pres.charts.PIE, [{
  name: "シェア", labels: ["A", "B", "その他"],
  values: [35, 45, 20]
}], {
  x: 7, y: 1, w: 5, h: 4,
  showPercent: true
});
```

---

## 画像

```javascript
// URL から
slide.addImage({ path: "https://example.com/image.png", x: 1, y: 1, w: 4, h: 3 });

// Base64 から
slide.addImage({ data: "image/png;base64,iVBORw...", x: 1, y: 1, w: 4, h: 3 });

// アスペクト比を保持するサイズ計算
function fitImage(origW, origH, maxW, maxH) {
  const ratio = Math.min(maxW / origW, maxH / origH);
  return { w: origW * ratio, h: origH * ratio };
}
```

---

## スライドマスター

```javascript
pres.defineSlideMaster({
  title: "TITLE_SLIDE",
  background: { color: "283A5E" },
  objects: [{
    placeholder: {
      options: { name: "title", type: "title", x: 1, y: 2, w: 8, h: 2 }
    }
  }]
});

let titleSlide = pres.addSlide({ masterName: "TITLE_SLIDE" });
titleSlide.addText("タイトル", { placeholder: "title" });
```

---

## よくある落とし穴

1. **`#` 付きカラーは使わない** — ファイル破損の原因
   ```javascript
   color: "FF0000"      // ✅
   color: "#FF0000"     // ❌
   ```

2. **8桁hex で透過を指定しない** — ファイル破損。`opacity` プロパティを使う
   ```javascript
   shadow: { color: "00000020" }                    // ❌
   shadow: { color: "000000", opacity: 0.12 }       // ✅
   ```

3. **Unicode の箇条書き記号（•）を使わない** — `bullet: true` を使う

4. **配列テキストでは `breakLine: true` が必要**

5. **オプションオブジェクトを再利用しない** — PptxGenJS は内部で値を変換するため破損する
   ```javascript
   // ❌ 2回目の呼び出しで変換済みの値が渡される
   const shadow = { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 };
   slide.addShape(pres.shapes.RECTANGLE, { shadow, ... });
   slide.addShape(pres.shapes.RECTANGLE, { shadow, ... });

   // ✅ 毎回新しいオブジェクトを生成
   const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 });
   slide.addShape(pres.shapes.RECTANGLE, { shadow: makeShadow(), ... });
   ```

6. **`ROUNDED_RECTANGLE` にアクセントバーを重ねない** — 角が覆えない。`RECTANGLE` を使う

7. **影の `offset` に負の値を使わない** — ファイル破損。上向きの影は `angle: 270` で

8. **プレゼンテーション毎に新しいインスタンスを作る** — `pptxgen()` オブジェクトの使い回し禁止

---

## クイックリファレンス

- **図形**: `RECTANGLE`, `OVAL`, `LINE`, `ROUNDED_RECTANGLE`
- **チャート**: `BAR`, `LINE`, `PIE`, `DOUGHNUT`, `SCATTER`, `BUBBLE`, `RADAR`
- **レイアウト**: `LAYOUT_16x9`, `LAYOUT_16x10`, `LAYOUT_4x3`, `LAYOUT_WIDE`
- **配置**: `"left"`, `"center"`, `"right"`
