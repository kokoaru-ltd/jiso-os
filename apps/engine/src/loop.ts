/**
 * JISO /loop ワーカー（骨格）
 * 周回: 観測 → 計画 → 稟議起票/執行 → 答え合わせ
 * 原則: 費用ゼロのアクションは自動実行 / 費用が発生するものは必ず稟議(pending)を起票して停止
 */
type Stage = "awareness"|"trust"|"contact"|"negotiation"|"order"|"delivery"|"invoice"|"repeat";

interface Observation { stage: Stage; metric: string; value: number; target: number; }
interface RingiDraft {
  title: string; filed_by: string; amount_yen: number; purpose: string;
  kpi_metric: string; kpi_delta: number; expected_roi_pct: number;
  poc_design: string; exit_condition: string;
}

export async function loopOnce(/* supabase client */) {
  const obs = await observe();          // 1. KPI観測（Supabase + 広告API + 架電ログ）
  const gaps = detectGaps(obs);         // 2. 目標との乖離検知
  for (const gap of gaps) {
    const plan = await planAction(gap); // 3. 打ち手生成（LLM + funnel係数）
    if (plan.amount_yen === 0) {
      await execute(plan);              // 4a. 無料アクション: 即実行
    } else {
      await fileRingi(toRingi(plan));   // 4b. 有料アクション: 稟議起票 → 人間の承認待ち
    }
  }
  await verifyCompleted();              // 5. 完了稟議の試算vs実測を記録
}

// --- 各関数の実装は次周回 ---
async function observe(): Promise<Observation[]> { return []; }
function detectGaps(o: Observation[]) { return o.filter(x => x.value < x.target); }
async function planAction(gap: Observation): Promise<any> { return { amount_yen: 0 }; }
async function execute(plan: any) {}
function toRingi(plan: any): RingiDraft { return plan; }
async function fileRingi(r: RingiDraft) {}
async function verifyCompleted() {}
