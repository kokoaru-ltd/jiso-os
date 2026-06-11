# INCAGENT Company Strategy

## Core Thesis

INCAGENT is not a resale tool, CRM, sales assistant, ad tool, or workflow automation app.

INCAGENT is an autonomous company operating system.

The user gives three things:

1. Goal
2. Budget
3. Approval authority boundaries

INCAGENT turns them into an operating loop:

1. Choose a business action
2. Research the market
3. Draft the plan
4. Ask humans only where approval or physical work is required
5. Execute
6. Measure
7. Learn
8. Decide the next action

Resale is only one possible first experiment because it creates visible profit and loss quickly.
The long-term company is category-agnostic: it should run sales, marketing, CRM, operations,
purchasing, invoicing, customer success, and reporting as one system.

## What We Are Building

Existing SaaS products are departmental tools.

- Salesforce owns CRM records and pipeline workflows.
- HubSpot owns marketing and sales automation.
- Shopify owns storefront operations.
- QuickBooks and freee own accounting workflows.
- Notion and Airtable own internal coordination.
- Zapier and Make own glue.

INCAGENT should not become one more branch.

INCAGENT should sit above the branches and decide what needs to happen next across the whole
company. CRM, ads, invoices, purchase orders, inventory, email, X posts, landing pages, and
human tasks are execution surfaces. They are not the source of truth.

The source of truth is the operating loop:

Goal -> Constraints -> Action proposal -> Approval -> Execution -> Result -> Next action

## Product Promise

Japanese:

やりたいこと、予算、権限だけ渡す。INCAGENTが告知、広告、営業、CRM、仕入れ、請求、改善まで一気通貫で回す。人間が必要な場所だけ、稟議または作業指示として人間に戻す。

English:

Give INCAGENT a goal, a budget, and authority limits. It runs awareness, ads, sales, CRM,
purchasing, invoicing, and optimization end to end. Humans are pulled in only for approvals,
physical work, legal decisions, and high-risk judgment.

## The Company Layer Model

### 1. Goal Layer

The founder writes an outcome, not a task list.

Examples:

- Turn JPY 100,000 into measurable profit within 90 days.
- Get 10 qualified discovery calls for a new service.
- Sell the first 30 units of a new product.
- Recover dormant customers.
- Launch a paid beta for a SaaS product.

The system converts this into target metrics:

- Revenue
- Gross margin
- Cash limit
- CAC
- Lead count
- Conversion rate
- Inventory turnover
- Payback period
- Deadline

### 2. Capital Layer

INCAGENT cannot move money freely.

Every paid action must become a proposal with:

- Amount
- Vendor or marketplace
- Expected return
- Evidence used
- Downside
- Stop condition
- Human task required
- Deadline for review

No approval means no spend.

### 3. Market Layer

INCAGENT continuously gathers market evidence.

For resale:

- Sold prices
- Listing velocity
- Fees
- Shipping cost
- Defect risk
- Competitor supply

For service businesses:

- Target customer list
- Existing pain
- Budget signal
- Competitor positioning
- Outreach channel
- Close probability

For SaaS:

- Pain intensity
- Existing tool stack
- Replacement difficulty
- Workflow frequency
- Buyer role
- Integration burden

### 4. Execution Layer

Execution should be modular, but governed by one operating loop.

Modules:

- SNS and announcements
- Paid ads
- Landing pages
- Outreach
- CRM updates
- Sales follow-up
- Proposal generation
- Purchase and procurement
- Inventory tracking
- Listing and pricing
- Invoice and payment follow-up
- Customer support
- Weekly reporting

The key point: these are not separate products. They are limbs.

### 5. Human Task Layer

When the system cannot or should not act alone, it creates human tasks.

Human task examples:

- Pay this invoice.
- Buy these units from this supplier.
- Check product condition.
- Pack and ship this item.
- Call this customer.
- Approve this ad spend.
- Confirm legal wording.
- Decide whether to take a loss.

Every human task must include:

- Why this task exists
- Exact action
- Deadline
- Expected business impact
- What happens if ignored

### 6. Memory and CRM Layer

CRM is not the product. CRM is memory.

INCAGENT records:

- People
- Companies
- Conversations
- Offers
- Objections
- Follow-ups
- Purchases
- Support issues
- Trust level
- Next best action

The system should not ask "what should we do with this lead?" It should already propose the next
action based on the goal and history.

### 7. Measurement Layer

Every action is audited against results.

Required fields:

- Prediction
- Actual result
- Variance
- Reason
- Next adjustment
- Confidence score

This prevents the company from becoming AI theater. Forecasts must survive contact with numbers.

## Why This Can Beat Traditional SaaS

Traditional SaaS assumes humans are the operators.

Humans log into CRM, write campaigns, check dashboards, move deals, send invoices, and coordinate
work. The software stores and routes the work.

INCAGENT assumes AI is the operator.

Humans provide capital, approval, physical execution, and judgment. The system decides, drafts,
routes, executes, measures, and improves.

This changes the buyer value:

- Old SaaS: "Use this tool to do your work."
- INCAGENT: "Give the system a goal and budget. It will run the work and ask only when blocked."

## Initial Market Entry

The first market should not be "all companies."

It should be owner-operated small businesses where:

- The founder controls decisions.
- Workflows are messy but not regulated like banking or healthcare.
- Revenue impact is visible.
- Existing SaaS usage is low or fragmented.
- Manual follow-up is a bottleneck.

Best first candidates:

1. Resale and small commerce
2. Local service businesses
3. B2B micro-agencies
4. Solo consultants
5. Small import/export operators

Avoid at first:

- Enterprise CRM replacement
- Regulated finance
- Medical operations
- Large-company procurement
- Deep ERP replacement

The Salesforce-level ambition is correct, but the entry wedge must be narrower.

## Public Experiment Format

The public experiment should show the operating loop, not just resale.

Weekly public report:

- Goal
- Budget remaining
- Actions proposed by AI
- Human approvals
- Human tasks
- Spend
- Revenue
- Profit/loss
- Mistakes
- Next week's plan

This format proves the company OS regardless of the business category.

## Business Model

### Phase 1: Proof

Run internal public businesses with small budgets.

Revenue:

- Product resale or service revenue
- Content-driven audience
- Paid teardown reports

### Phase 2: Assisted Operations

Sell INCAGENT as a managed operating layer for small businesses.

Pricing:

- Setup fee
- Monthly retainer
- Performance bonus where legally and operationally appropriate

### Phase 3: Software Platform

Turn repeated operating loops into SaaS.

Pricing:

- Monthly base subscription
- Seatless usage pricing
- Spend-governance tier
- Workflow module pricing
- Enterprise controls later

### Phase 4: Company Autopilot

The long-term product is a cross-functional company autopilot.

At this stage, Salesforce, HubSpot, ad platforms, accounting tools, and commerce platforms are
connected execution surfaces. INCAGENT owns the decision loop.

## Non-Negotiable Product Rules

1. No money moves without approval.
2. Every paid action has expected return and stop condition.
3. Every forecast is compared with actual results.
4. Every human task must be specific enough to execute.
5. The system must explain why it chose an action.
6. The system must remember customer and company context.
7. The system must prefer real revenue proof over platform features.
8. The system must not become a dashboard.

## Immediate Next Build

Build the first end-to-end loop:

1. User sets goal and budget.
2. INCAGENT researches possible business actions.
3. INCAGENT creates three proposals.
4. Human approves one.
5. INCAGENT creates SNS announcement, landing copy, outreach list, and execution tasks.
6. Human performs physical or payment tasks.
7. INCAGENT records spend and outcome.
8. INCAGENT publishes a weekly report.

This is the smallest version of the company.

