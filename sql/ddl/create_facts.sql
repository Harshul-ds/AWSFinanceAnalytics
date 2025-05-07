-- Amazon Redshift DDL for Fact Tables
-- Placeholder - Actual schema will depend on specific requirements

-- Fact Table: FactFinancials
CREATE TABLE IF NOT EXISTS FactFinancials (
    TransactionID VARCHAR(100), -- From source, if available, or generated
    DateKey INT NOT NULL DISTKEY SORTKEY, -- Foreign Key to DimDate
    DepartmentKey INT NOT NULL, -- Foreign Key to DimDepartment
    AccountKey INT NOT NULL,    -- Foreign Key to DimAccount
    ScenarioKey INT NOT NULL,   -- Foreign Key to DimScenario
    Amount DECIMAL(18, 2) NOT NULL,
    BudgetAmount DECIMAL(18, 2),
    VarianceAmount DECIMAL(18, 2), -- Calculated as Amount - BudgetAmount
    CurrencyCode VARCHAR(3) DEFAULT 'USD',
    TransactionDate DATE, -- Original transaction date from source, useful for some analyses
    LoadTimestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT GETDATE() -- Timestamp of when the record was loaded
    -- PRIMARY KEY (TransactionID, DateKey, DepartmentKey, AccountKey, ScenarioKey) -- Composite PK, consider if TransactionID is unique enough or needs to be part of it
)
DISTSTYLE KEY
DISTKEY (DateKey) -- Common join key
COMPOUND SORTKEY (DateKey, DepartmentKey, AccountKey, ScenarioKey); -- Common filter/join columns

-- Foreign Key Constraints (Redshift enforces them for query optimization, not during load by default)
-- ALTER TABLE FactFinancials ADD CONSTRAINT fk_date FOREIGN KEY (DateKey) REFERENCES DimDate (DateKey);
-- ALTER TABLE FactFinancials ADD CONSTRAINT fk_department FOREIGN KEY (DepartmentKey) REFERENCES DimDepartment (DepartmentKey);
-- ALTER TABLE FactFinancials ADD CONSTRAINT fk_account FOREIGN KEY (AccountKey) REFERENCES DimAccount (AccountKey);
-- ALTER TABLE FactFinancials ADD CONSTRAINT fk_scenario FOREIGN KEY (ScenarioKey) REFERENCES DimScenario (ScenarioKey);

-- Notes:
-- 1. Choose DISTKEY and SORTKEYs based on query patterns. The ones above are common starting points.
--    - DISTKEY (DateKey) might be good if many queries join/filter by date.
--    - COMPOUND SORTKEY helps with queries filtering on the leading columns of the sort key.
-- 2. Redshift's `COPY` command is generally used for bulk loading and bypasses FK enforcement for speed.
--    Data integrity should be ensured during the ETL process.
-- 3. `TransactionID` can be a natural key from the source system or a generated one if multiple sources are combined.
--    If it's not unique across all dimensions, the composite PK might be more complex.
-- 4. `VarianceAmount` can be calculated in ETL or as a computed column if Redshift version supports it well for your use case.
--    Typically, it's pre-calculated in ETL for performance.
