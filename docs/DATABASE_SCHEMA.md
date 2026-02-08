# 🗄️ DATABASE SCHEMA - Freedom Wallet Bot

## Overview
Thiết kế database cho viral growth, education, conversion, retention tracking.

---

## 📊 CORE TABLES

### **1. users** (Thông tin người dùng chính)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    full_name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    
    -- User state (BẢN CHẤT - không đổi thường xuyên)
    user_state VARCHAR(50) DEFAULT 'VISITOR',
    -- Core states: VISITOR, REGISTERED, VIP, SUPER_VIP, ADVOCATE
    -- ⚠️ KHÔNG dùng NURTURE_DAY_X, ONBOARDING_DAY_X ở đây!
    
    -- Current program (CHƯƠNG TRÌNH - có thể tham gia nhiều)
    current_program VARCHAR(50),
    -- Programs: NURTURE_CAMPAIGN, ONBOARDING_7_DAY, MENTOR_PROGRAM, AFFILIATE_PROGRAM
    
    program_day INTEGER DEFAULT 0,
    -- Day progress in current program (0-7 for onboarding)
    
    program_started_at TIMESTAMP,
    program_completed_at TIMESTAMP
    
    -- Referral tracking
    referral_code VARCHAR(20) UNIQUE,
    referrer_id INTEGER,
    referral_count INTEGER DEFAULT 0,
    
    -- Segmentation
    user_segment VARCHAR(20),
    -- Segments: STUDENT, WORKING, INVESTOR
    
    -- Activation status
    activation_status VARCHAR(20) DEFAULT 'PENDING',
    -- Status: PENDING, IN_PROGRESS, COMPLETED, ABANDONED
    activation_checklist JSONB,
    -- JSON: {"task_1": true, "task_2": false, ...}
    
    -- Education tracking
    quiz_score INTEGER DEFAULT 0,
    onboarding_day INTEGER DEFAULT 0,
    certificate_issued BOOLEAN DEFAULT FALSE,
    
    -- Badges & achievements
    badges JSONB,
    -- JSON: ["first_success", "rising_star", "super_vip"]
    
    -- Revenue sharing (Super VIP)
    revenue_share_enabled BOOLEAN DEFAULT FALSE,
    revenue_share_rate DECIMAL(5,2) DEFAULT 0.00,
    -- 40.00 for Super VIP
    
    -- Super VIP decay tracking
    super_vip_last_active TIMESTAMP,
    super_vip_decay_warned BOOLEAN DEFAULT FALSE,
    -- TRUE if user warned about 14-day inactivity
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    vip_unlocked_at TIMESTAMP,
    super_vip_unlocked_at TIMESTAMP,
    
    FOREIGN KEY (referrer_id) REFERENCES users(id)
);

CREATE INDEX idx_user_state ON users(user_state);
CREATE INDEX idx_referral_code ON users(referral_code);
CREATE INDEX idx_referrer_id ON users(referrer_id);
CREATE INDEX idx_user_segment ON users(user_segment);
```

---

### **2. referrals** (Chi tiết giới thiệu)

```sql
CREATE TABLE referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id INTEGER NOT NULL,
    referred_id INTEGER NOT NULL,
    
    -- Tracking
    clicked_at TIMESTAMP,
    registered_at TIMESTAMP,
    conversion_time INTEGER,
    -- Seconds from click to registration
    
    -- Status
    is_valid BOOLEAN DEFAULT TRUE,
    -- FALSE if suspected fraud
    
    -- Fraud detection
    ip_address VARCHAR(50),
    user_agent TEXT,
    device_fingerprint VARCHAR(255),
    -- Hash of device info for duplicate detection
    
    -- Source tracking
    source VARCHAR(50),
    -- telegram, zalo, facebook, etc.
    
    campaign_id VARCHAR(50),
    -- For A/B testing different messages
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (referrer_id) REFERENCES users(id),
    FOREIGN KEY (referred_id) REFERENCES users(id),
    UNIQUE(referrer_id, referred_id)
);

CREATE INDEX idx_referrer ON referrals(referrer_id);
CREATE INDEX idx_referred ON referrals(referred_id);
```

---

### **3. quiz_attempts** (Lịch sử quiz)

```sql
CREATE TABLE quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- Quiz info
    quiz_day INTEGER NOT NULL,
    question_id VARCHAR(50) NOT NULL,
    
    -- Answer
    user_answer VARCHAR(10),
    correct_answer VARCHAR(10),
    is_correct BOOLEAN,
    
    -- Scoring
    points_awarded INTEGER DEFAULT 0,
    
    -- Retry tracking
    attempt_number INTEGER DEFAULT 1,
    
    -- Timing
    time_to_answer INTEGER,
    -- Seconds from question sent to answer
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_user_quiz ON quiz_attempts(user_id, quiz_day);
```

---

### **4. activation_tasks** (Chi tiết checklist)

```sql
CREATE TABLE activation_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- Task info
    task_id VARCHAR(50) NOT NULL,
    -- task_1 to task_5
    
    task_name VARCHAR(255),
    -- "Copy template", "First income", etc.
    
    -- Status
    status VARCHAR(20) DEFAULT 'PENDING',
    -- PENDING, IN_PROGRESS, COMPLETED, SKIPPED
    
    -- Proof
    screenshot_url VARCHAR(500),
    proof_verified BOOLEAN,
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, task_id)
);

CREATE INDEX idx_user_tasks ON activation_tasks(user_id);
CREATE INDEX idx_task_status ON activation_tasks(status);
```

---

### **5. weekly_reports** (Báo cáo định kỳ)

```sql
CREATE TABLE weekly_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    -- Report period
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    
    -- Metrics (fetched from user's Google Sheet)
    total_income DECIMAL(15,2),
    total_expense DECIMAL(15,2),
    net_cashflow DECIMAL(15,2),
    
    -- Jars balance
    jar_nec DECIMAL(15,2),
    jar_lts DECIMAL(15,2),
    jar_edu DECIMAL(15,2),
    jar_play DECIMAL(15,2),
    jar_ffa DECIMAL(15,2),
    jar_give DECIMAL(15,2),
    
    -- Activity
    days_active INTEGER,
    transactions_count INTEGER,
    
    -- Comparison
    income_vs_last_week DECIMAL(5,2),
    -- Percentage change
    
    expense_vs_last_week DECIMAL(5,2),
    
    -- Engagement
    report_sent BOOLEAN DEFAULT FALSE,
    report_viewed BOOLEAN DEFAULT FALSE,
    report_shared BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_user_reports ON weekly_reports(user_id, week_start);
```

---

### **6. events** (Event tracking cho analytics)

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    
    -- Event details
    event_type VARCHAR(100) NOT NULL,
    -- button_click, message_sent, quiz_answer, share_link, etc.
    
    event_category VARCHAR(50),
    -- viral, education, retention, conversion
    
    event_data JSONB,
    -- Flexible JSON for extra data
    
    -- Context
    session_id VARCHAR(100),
    source VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_event_type ON events(event_type);
CREATE INDEX idx_event_category ON events(event_category);
CREATE INDEX idx_user_events ON events(user_id, created_at);
```

---

### **7. super_vip_config** (Cấu hình Super VIP slots)

```sql
CREATE TABLE super_vip_config (
    id INTEGER PRIMARY KEY,
    
    -- Limits
    total_slots INTEGER DEFAULT 100,
    slots_filled INTEGER DEFAULT 0,
    
    -- Requirements
    referral_threshold INTEGER DEFAULT 50,
    revenue_share_rate DECIMAL(5,2) DEFAULT 40.00,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default config
INSERT INTO super_vip_config (id, total_slots, slots_filled, referral_threshold, revenue_share_rate)
VALUES (1, 100, 0, 50, 40.00);
```

---

### **8. content_library** (Nội dung động)

```sql
CREATE TABLE content_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Content type
    content_type VARCHAR(50),
    -- tip, tutorial, quiz_question, certificate_template
    
    -- Segmentation
    target_segment VARCHAR(20),
    -- STUDENT, WORKING, INVESTOR, ALL
    
    -- Content
    title VARCHAR(255),
    body TEXT,
    media_url VARCHAR(500),
    
    -- Quiz specific
    question_text TEXT,
    options JSONB,
    -- JSON: [{"A": "50%"}, {"B": "55%"}, {"C": "60%"}]
    
    correct_answer VARCHAR(10),
    explanation TEXT,
    
    -- Scheduling
    schedule_type VARCHAR(20),
    -- daily, weekly, onboarding_day_X
    
    schedule_day INTEGER,
    -- For onboarding: 1-7
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_content_type ON content_library(content_type);
CREATE INDEX idx_target_segment ON content_library(target_segment);
```

---

## 🔗 RELATIONSHIPS DIAGRAM

```
users (1) ──< (N) referrals (referrer_id)
users (1) ──< (N) referrals (referred_id)
users (1) ──< (N) quiz_attempts
users (1) ──< (N) activation_tasks
users (1) ──< (N) weekly_reports
users (1) ──< (N) events
```

---

## 📈 KEY METRICS QUERIES

### **Viral Growth Metrics**

```sql
-- Referral conversion rate
SELECT 
    COUNT(DISTINCT referrer_id) as total_referrers,
    COUNT(DISTINCT referred_id) as total_referred,
    ROUND(COUNT(DISTINCT referred_id) * 100.0 / COUNT(DISTINCT referrer_id), 2) as conversion_rate
FROM referrals
WHERE registered_at IS NOT NULL;

-- Top referrers (Leaderboard)
SELECT 
    u.full_name,
    u.referral_count,
    u.user_state,
    u.badges
FROM users u
ORDER BY u.referral_count DESC
LIMIT 10;

-- Super VIP slots remaining
SELECT 
    (total_slots - slots_filled) as slots_remaining
FROM super_vip_config
WHERE id = 1;
```

### **Education Metrics**

```sql
-- Quiz completion rate by day
SELECT 
    quiz_day,
    COUNT(DISTINCT user_id) as users_attempted,
    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_answers,
    ROUND(SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as accuracy_rate
FROM quiz_attempts
GROUP BY quiz_day;

-- Certificate issuance rate
SELECT 
    COUNT(CASE WHEN certificate_issued = 1 THEN 1 END) as certificates_issued,
    COUNT(*) as total_vip_users,
    ROUND(COUNT(CASE WHEN certificate_issued = 1 THEN 1 END) * 100.0 / COUNT(*), 2) as issuance_rate
FROM users
WHERE user_state >= 'VIP';
```

### **Conversion Metrics**

```sql
-- Activation completion rate
SELECT 
    activation_status,
    COUNT(*) as user_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM users
WHERE user_state >= 'VIP'
GROUP BY activation_status;

-- Average time to activate
SELECT 
    AVG(JULIANDAY(completed_at) - JULIANDAY(started_at)) as avg_days_to_complete
FROM activation_tasks
WHERE status = 'COMPLETED';
```

### **Retention Metrics**

```sql
-- Weekly active users
SELECT 
    DATE(last_active, 'weekday 0', '-6 days') as week_start,
    COUNT(DISTINCT user_id) as weekly_active_users
FROM users
WHERE last_active >= DATE('now', '-30 days')
GROUP BY week_start
ORDER BY week_start;

-- Churn rate (no activity 30+ days)
SELECT 
    COUNT(CASE WHEN last_active < DATE('now', '-30 days') THEN 1 END) as churned_users,
    COUNT(*) as total_users,
    ROUND(COUNT(CASE WHEN last_active < DATE('now', '-30 days') THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate
FROM users
WHERE user_state >= 'VIP';
```

---

## 🔄 MIGRATION PLAN

### **Phase 1: Extend existing tables**
- Add new columns to `users` table
- Create indexes for performance

### **Phase 2: Create new tables**
- `quiz_attempts`
- `activation_tasks`
- `super_vip_config`

### **Phase 3: Add advanced tables**
- `weekly_reports`
- `events`
- `content_library`

### **Phase 4: Optimize**
- Switch to PostgreSQL when users > 10k
- Add materialized views for analytics
- Implement Redis cache for leaderboard
