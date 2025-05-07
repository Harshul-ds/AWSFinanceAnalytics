-- Amazon Redshift DDL for Dimension Tables
-- Placeholder - Actual schema will depend on specific requirements

-- Dimension: DimDate
CREATE TABLE IF NOT EXISTS DimDate (
    DateKey INT PRIMARY KEY DISTKEY SORTKEY,
    FullDate DATE NOT NULL,
    Year SMALLINT NOT NULL,
    Quarter SMALLINT NOT NULL,
    Month SMALLINT NOT NULL,
    MonthName VARCHAR(20) NOT NULL,
    DayOfMonth SMALLINT NOT NULL,
    DayOfWeekName VARCHAR(20) NOT NULL,
    WeekOfYear SMALLINT,
    IsWeekend BOOLEAN
);

-- Dimension: DimDepartment
CREATE TABLE IF NOT EXISTS DimDepartment (
    DepartmentKey INT PRIMARY KEY DISTKEY SORTKEY,
    DepartmentID VARCHAR(50) NOT NULL, -- Natural key from source
    DepartmentName VARCHAR(255) NOT NULL,
    BusinessUnit VARCHAR(255),
    CostCenter VARCHAR(100),
    EffectiveStartDate DATE,
    EffectiveEndDate DATE,
    IsCurrent BOOLEAN
);

-- Dimension: DimAccount
CREATE TABLE IF NOT EXISTS DimAccount (
    AccountKey INT PRIMARY KEY DISTKEY SORTKEY,
    AccountID VARCHAR(50) NOT NULL, -- Natural key from source
    AccountName VARCHAR(255) NOT NULL,
    AccountType VARCHAR(100) NOT NULL, -- e.g., Revenue, Expense, Asset, Liability, Equity
    AccountSubType VARCHAR(100),
    ChartOfAccountsCategory VARCHAR(100),
    EffectiveStartDate DATE,
    EffectiveEndDate DATE,
    IsCurrent BOOLEAN
);

-- Dimension: DimScenario
CREATE TABLE IF NOT EXISTS DimScenario (
    ScenarioKey INT PRIMARY KEY DISTKEY SORTKEY,
    ScenarioName VARCHAR(100) NOT NULL UNIQUE, -- e.g., 'Actual', 'Budget', 'Forecast Q1'
    Description VARCHAR(255)
);

-- Note: For production, consider appropriate DISTSTYLE and SORTKEY strategies based on query patterns.
-- For example, DISTSTYLE ALL for smaller dimension tables, DISTSTYLE KEY for larger ones on their PKs.
-- SORTKEYs should be chosen based on common filter/join columns.
