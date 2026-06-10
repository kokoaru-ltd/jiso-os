-- JISO 稟議エンジン 初期スキーマ（適用済み: Supabase project wckfqfjzpmjkznhnfaqb, schema "loop"）
create schema if not exists loop;

create table loop.goals (
  id uuid primary key default gen_random_uuid(),
  company_name text not null,
  intent text not null,
  kpi_tree jsonb,
  industry text,
  status text not null default 'active' check (status in ('active','paused','archived')),
  created_at timestamptz not null default now()
);

create table loop.ringi (
  id bigint generated always as identity primary key,
  goal_id uuid references loop.goals(id) on delete cascade,
  title text not null,
  filed_by text not null,
  amount_yen integer not null check (amount_yen >= 0),
  purpose text not null,
  kpi_metric text not null,
  kpi_delta numeric,
  expected_roi_pct numeric,
  expected_gross_profit_yen integer,
  poc_design text,
  exit_condition text not null,
  status text not null default 'pending'
    check (status in ('pending','approved','rejected','executing','completed','stopped')),
  decided_at timestamptz,
  decided_by text,
  created_at timestamptz not null default now()
);

create table loop.ringi_results (
  id bigint generated always as identity primary key,
  ringi_id bigint not null references loop.ringi(id) on delete cascade,
  actual_spend_yen integer,
  actual_revenue_yen integer,
  actual_roi_pct numeric,
  variance_pct numeric,
  note text,
  measured_at timestamptz not null default now()
);

create table loop.human_tasks (
  id bigint generated always as identity primary key,
  goal_id uuid references loop.goals(id) on delete cascade,
  ringi_id bigint references loop.ringi(id) on delete set null,
  title text not null,
  instructions text not null,
  reason text not null,
  cost_yen integer default 0,
  due_at timestamptz,
  status text not null default 'open' check (status in ('open','in_progress','done','cancelled')),
  created_at timestamptz not null default now()
);

create table loop.audit_log (
  id bigint generated always as identity primary key,
  agent text not null,
  action text not null,
  detail jsonb,
  cost_yen integer default 0,
  created_at timestamptz not null default now()
);

create index idx_ringi_status on loop.ringi(status);
create index idx_human_tasks_status on loop.human_tasks(status);
create index idx_audit_log_created on loop.audit_log(created_at);

alter table loop.goals enable row level security;
alter table loop.ringi enable row level security;
alter table loop.ringi_results enable row level security;
alter table loop.human_tasks enable row level security;
alter table loop.audit_log enable row level security;
