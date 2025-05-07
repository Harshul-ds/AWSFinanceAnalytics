-- Amazon Redshift DML - Sample Queries
-- These queries assume the Star Schema (DimDate, DimDepartment, DimAccount, DimScenario, FactFinancials) is populated.

-- 1. Total Actual Amount per Department for a specific Year
SELECT
    d.DepartmentName,
    SUM(f.Amount) AS TotalActualAmount
FROM FactFinancials f
JOIN DimDepartment d ON f.DepartmentKey = d.DepartmentKey
JOIN DimDate dt ON f.DateKey = dt.DateKey
JOIN DimScenario s ON f.ScenarioKey = s.ScenarioKey
WHERE dt.Year = 2024 AND s.ScenarioName = 'Actual'
GROUP BY d.DepartmentName
ORDER BY TotalActualAmount DESC;

-- 2. Monthly Actual vs. Budget Variance for a specific Account Type
SELECT
    dt.Year,
    dt.MonthName,
    da.AccountType,
    SUM(CASE WHEN ds.ScenarioName = 'Actual' THEN f.Amount ELSE 0 END) AS TotalActual,
    SUM(CASE WHEN ds.ScenarioName = 'Budget' THEN f.BudgetAmount ELSE 0 END) AS TotalBudget,
    SUM(CASE WHEN ds.ScenarioName = 'Actual' THEN f.Amount ELSE 0 END) - SUM(CASE WHEN ds.ScenarioName = 'Budget' THEN f.BudgetAmount ELSE 0 END) AS Variance
FROM FactFinancials f
JOIN DimDate dt ON f.DateKey = dt.DateKey
JOIN DimAccount da ON f.AccountKey = da.AccountKey
JOIN DimScenario ds ON f.ScenarioKey = ds.ScenarioKey
WHERE da.AccountType = 'Expense' AND dt.Year = 2024
GROUP BY dt.Year, dt.MonthName, da.AccountType
ORDER BY dt.Year, dt.MonthName;

-- 3. Top 5 Accounts with Highest Actual Spending in a Quarter
SELECT
    da.AccountName,
    SUM(f.Amount) AS QuarterlySpending
FROM FactFinancials f
JOIN DimAccount da ON f.AccountKey = da.AccountKey
JOIN DimDate dt ON f.DateKey = dt.DateKey
JOIN DimScenario ds ON f.ScenarioKey = ds.ScenarioKey
WHERE dt.Year = 2024 AND dt.Quarter = 1 AND ds.ScenarioName = 'Actual'
GROUP BY da.AccountName
ORDER BY QuarterlySpending DESC
LIMIT 5;

-- 4. Variance Percentage by Department and Account Category
SELECT 
    dd.DepartmentName,
    da.ChartOfAccountsCategory,
    SUM(CASE WHEN ds.ScenarioName = 'Actual' THEN ff.Amount ELSE 0 END) AS ActualAmount,
    SUM(CASE WHEN ds.ScenarioName = 'Budget' THEN ff.BudgetAmount ELSE 0 END) AS BudgetedAmount,
    CASE 
        WHEN SUM(CASE WHEN ds.ScenarioName = 'Budget' THEN ff.BudgetAmount ELSE 0 END) = 0 THEN NULL -- Avoid division by zero
        ELSE (SUM(CASE WHEN ds.ScenarioName = 'Actual' THEN ff.Amount ELSE 0 END) - SUM(CASE WHEN ds.ScenarioName = 'Budget' THEN ff.BudgetAmount ELSE 0 END)) * 100.0 / SUM(CASE WHEN ds.ScenarioName = 'Budget' THEN ff.BudgetAmount ELSE 0 END)
    END AS VariancePercentage
FROM FactFinancials ff
JOIN DimDepartment dd ON ff.DepartmentKey = dd.DepartmentKey
JOIN DimAccount da ON ff.AccountKey = da.AccountKey
JOIN DimDate d ON ff.DateKey = d.DateKey
JOIN DimScenario ds ON ff.ScenarioKey = ds.ScenarioKey
WHERE d.Year = 2024
GROUP BY dd.DepartmentName, da.ChartOfAccountsCategory
ORDER BY dd.DepartmentName, VariancePercentage DESC;

-- 5. Running Total of Actual Expenses for a Department
SELECT 
    d.FullDate,
    dept.DepartmentName,
    f.Amount AS DailyAmount,
    SUM(f.Amount) OVER (PARTITION BY dept.DepartmentName ORDER BY d.FullDate ASC ROWS UNBOUNDED PRECEDING) AS RunningTotalExpenses
FROM FactFinancials f
JOIN DimDate d ON f.DateKey = d.DateKey
JOIN DimDepartment dept ON f.DepartmentKey = dept.DepartmentKey
JOIN DimScenario s ON f.ScenarioKey = s.ScenarioKey
JOIN DimAccount acc ON f.AccountKey = acc.AccountKey
WHERE dept.DepartmentName = 'Office Supplies Purchase' -- Example Department Name
  AND s.ScenarioName = 'Actual'
  AND acc.AccountType = 'Expense'
  AND d.Year = 2024
ORDER BY dept.DepartmentName, d.FullDate;
