/* ============================================================
   サイト設定 — ここだけ編集すれば動作を切り替えられます
   ============================================================ */
window.PBM_CONFIG = {
  siteName: "Power BI Mastery",

  /* 学習ログ / アクセス統計の収集先（Cloudflare Worker のURL）
     空文字のままなら計測は完全に無効（何も送信しません）。
     例: "https://pbm-analytics.<あなたのサブドメイン>.workers.dev"        */
  analyticsEndpoint: "",

  /* 計測を有効にするか（endpoint が空なら無視される） */
  analyticsEnabled: true,

  /* 滞在時間の送信間隔(秒)。ページ離脱時にも送信します。 */
  heartbeatSeconds: 30,

  /* 模擬試験の設定 */
  exam: { questions: 30, minutes: 45, passLine: 70 },

  /* 合格ラインとみなすレッスン内クイズの正答率(%) */
  quizPassLine: 80
};
