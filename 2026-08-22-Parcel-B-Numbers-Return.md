# Parcel B return — the essay numbers, adjudicated

*22 August 2026. **Mixed return: one item genuinely resolved, one in conflict, one built on
verifiably wrong parent figures but carrying a valuable structural finding anyway.** Read §3
before using anything from task 3.*

---

## 1. C-024 IS RESOLVED — and the design that resolved it is the transferable lesson

**The three conflicting margin-debt figures were never a contradiction. They are three different
(numerator vintage × denominator choice) combinations, and all three are arithmetically correct
for what they measure:**

| Figure | What it actually is |
|---|---|
| **1.756%** | March 2026 FINRA debit balances **$1,220,922m** ÷ 2026Q1 Z.1 non-financial corporate equity **$69,511,628m** |
| **1.84%** | Either the **2025Q4 vintage** (Dec-2025 margin debt $1,225.6bn ÷ 2025Q4 NFC equity $66.52trn), **or** March-2026 margin debt over a **narrower index base** (Wilshire 5000 / Russell 3000, ~$66.3trn) |
| **0.90%** | The **all-sector** denominator — total corporate equity ~$135.5trn, which includes financial-sector equity, foreign equities held by US residents, and mutual-fund/ETF shares |

**Why this worked, and why it is worth copying.** The parcel required independent derivation
*before* revealing our three values, and explicitly instructed the model not to read ahead.
It derived 1.7564% from named series and only then explained the other two. **Asking "which of
these three is right?" would have produced agreement with one of them and settled nothing.**
This is the direct pay-off of C-045 and the design should be reused wherever we have competing
internal figures.

**The conceptual finding is arguably worth more than the resolution.** The ratio is
**structurally mismatched**: the numerator is customer debit balances collateralised by
*everything* in retail and wealth-management brokerage accounts — ETFs, closed-end funds, ADRs,
corporate and municipal bonds — while the denominator is domestic non-financial corporate equity
only. **A meaningful share of FINRA margin borrowing finances leveraged ETF and multi-asset
positions that are not US corporate equity at all.** We asked whether the ratio was conceptually
sound and the answer is that it is not, cleanly. *Use the flow, as §5 already said; if the level
is used at all, state the mismatch.*

**Long-run context returned** (unverified, but internally consistent and the two anchor points
are well-known): 2000Q1 1.59% · 2007Q2 1.70% · 2018–19 ~1.71% · **2021Q4 1.93%** · 2026Q1 1.756%.
Reading: upper quartile of a 25-year 1.10–1.93% range, at about the 2007 level, **below** the
2021 peak.

**One caution on reproducibility.** The denominator was given as **`FL103164103.Q`**. In Z.1,
market-value level series carry the **`LM`** prefix — the FRED mapping given (`NCBEILQ027S`)
corresponds to **`LM103164103`**. Check the prefix before anyone tries to pull it.

**Vintage archive:** FRED carries `MARGIN` (discontinued 2017) and `FINRAMARGIN`, plus Wayback
captures of the FINRA page. *Unverified, but it would solve the 31 Aug calendar item if true —
check before relying on the snapshot being necessary.*

---

## 2. Task 2 — A DIRECT CONFLICT WITH THE EARLIER EXTERNAL REVIEW

Two external reviewers now give **different values for the same BEA Table 5.1 line**:

| Gross private saving | 2019 | 2025 |
|---|---|---|
| **Grok** (21 Aug, accepted and carried in our documents) | **$4,815bn** | **$6,384bn** |
| **Gemini** (22 Aug, Table 5.1 line 20 = net private saving + private CFC) | **$5,066.0bn** | **$6,153.3bn** |

**Neither is verified by us.** Gemini's is at least internally consistent — its line 20 equals
its line 3 plus line 13 in every year — but that only shows the arithmetic is coherent, not that
the inputs are right.

**What survives regardless: the direction.** Both have gross private saving rising substantially
across the window — **+$1.09trn** on Gemini's numbers, **+$1.57trn** on Grok's. **The C-030 kill
does not depend on which is right**, because it rests on gross private saving having *risen*, not
on its level. That kill stands.

**What does not survive: the specific pair we have been quoting.** `$4,815bn → $6,384bn` appears
in `RESEARCH_STATE.md` §1.1, `CLAUDE.md` and the Gemini parcel. **It is now contested and must be
marked as such** until read off the BEA table directly. This is a one-lookup task and it is the
K6 item in §5, which is exactly what that item was for.

*Also returned, and useful if it holds:* private consumption of fixed capital rising $2.82trn →
$3.89trn across 2019–2026, i.e. **depreciation is ~62% of gross private saving**. Consistent in
spirit with our "72.1% of internal funds is CFC", though the denominators differ and the two must
not be conflated.

---

## 3. Task 3 — THE PARENT FIGURES ARE WRONG. THE STRUCTURAL FINDING IS EXCELLENT.

### The numbers, rejected

Gemini reports household net worth rising **~$21.4trn** over 2023–25, from ~$142.2trn (YE2022) to
**~$163.6trn (YE2025)**, with holding gains of **$16.3trn**.

**Verified by us against the Fed's own Z.1 releases, 22 Aug:** household and nonprofit net worth
was **$169.3trn at 2025Q1, $176.3trn at 2025Q2, $181.6trn at 2025Q3, and rose a further $2.2trn
in 2025Q4 — approximately $183.8trn at year-end 2025.**

**Gemini's YE2025 endpoint is roughly $20trn too low.** Its YE2022 start (~$142.2trn) is about
right, so the error is concentrated in the endpoint, which **halves the measured rise**. Our own
figures — a **$39.16trn** rise with **$31.40trn** of net holding gains on the 11 June 2026
vintage, previously confirmed by Grok — are consistent with ~$183.8trn and are the ones that
stand.

**Therefore every level in the task-3 decomposition table is rejected**, and with them the
component figures ($7.85trn direct equities, $2.20trn mutual funds, $3.60trn pensions, etc.).

### And note precisely how it failed — this is C-045 in a new form

The parcel said: *"Do not tell me whether 83.7% is right or wrong. Tell me what the accounts
publish."* The return nonetheless produced a component decomposition summing to
**$13.65trn / $16.30trn = 83.74%** — landing on the supplied figure to two decimal places, **on
top of a parent number that is $20trn wrong.**

**Confirmation of a supplied figure can survive arbitrarily large errors in the inputs**, because
the components can be fitted to the target. This is a sharper version of C-045 than the WP/11/289
case: there, agreement was uninformative; here, **agreement actively concealed a $20trn error.**

### What survives, and it is the most useful thing in the whole parcel

The **structural** answers do not depend on the levels, and they settle the question:

1. **The decomposition table is `R.101`** — *Change in Net Worth of Households and Nonprofit
   Organizations* — with the integrated-accounts revaluation account (S.3.a / S.3.q) as the
   secondary route. *Plausible and consistent with the Fed publishing a "Changes in Net Worth"
   data-viz table; verify the line numbers.*
2. **"Equity-linked" is NOT a category the Z.1 publishes.** It is an analytical composite. So the
   83.7% was never going to be found in a table — it has to be constructed, and the construction
   is a choice.
3. **The choice is pension entitlements, and it dominates the answer.** R.101 records the
   revaluation of the *entire* pension entitlement claim, not just its equity slice. So:
   - **including** pension entitlements → **83.7%**
   - **excluding** them → **61.7%**
   - **the 83.7% figure mathematically requires treating 100% of pension-reserve holding gains as
     equity-linked**, which is defensible only under the further assumption that fixed-income
     revaluations inside pensions were ~zero across the window.

**This is the finding.** Whatever the correct levels turn out to be, **the equity-linked share is
a 61.7%–83.7% range governed by a definitional choice, not a single measured quantity.** Shipping
"83.7% equity-linked" as a fact was never safe. → **C-046.**

---

## 4. What this changes

- **C-024 closed** — three figures explained; the level is conceptually unsound and the flow is
  what we use. § 5 item 1 can come off the blocking list.
- **C-046 opened** — the 83.7% is a range with a stated pension assumption, or it does not ship.
- **The Grok saving pair is now contested**, and K6 becomes a direct BEA lookup rather than a
  rewrite. The C-030 kill is unaffected.
- **Cross-parcel check available now.** Parcel A's overlap row 9 claimed prime-brokerage
  hedge-fund balances sit inside FINRA margin debt. Parcel B independently says the numerator is
  *customer* debit balances covering retail and wealth-management accounts, and never mentions
  prime brokerage. **The two returns disagree**, and they were produced independently — which is
  exactly the consistency test the split-parcel format makes possible. Resolve before either is
  used.
