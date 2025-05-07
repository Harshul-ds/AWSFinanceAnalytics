# AWS-Powered Unified Commerce Performance Analytics for Rapidly Scaling D2C Brands

## 🚀 Elevating a Growing Business: The Story of "ArtisanGlow"

**Imagine "ArtisanGlow,"** a direct-to-consumer (D2C) brand specializing in unique, artisanal home goods. They launched with a passion for quality and a savvy digital presence, initially selling through their own Shopify-powered e-commerce store. Fueled by effective social media marketing (Facebook/Instagram Ads, Google Ads) and word-of-mouth, ArtisanGlow has experienced **explosive growth.**

To further expand their market reach, they've strategically embraced the Amazon Marketplace, becoming a third-party seller. While this multi-channel approach has significantly boosted revenue, it has also unveiled a complex web of operational and analytical challenges for their lean finance and marketing teams.

This project, the **AWS-Powered Unified Commerce Performance Analytics Platform**, is architected as the solution to ArtisanGlow's critical growth pains, transforming their fragmented data landscape into a powerhouse for strategic decision-making.

## 🔥 The Challenge: Navigating Multi-Channel Complexity & Data Silos

ArtisanGlow, like many rapidly scaling D2C brands, found themselves grappling with critical pain points that threatened to stifle their growth and profitability:

1.  **Fragmented Data & The Elusive Single Source of Truth:**
    *   **Shopify Store:** Rich with sales transactions, customer details, discount code usage, and website analytics.
    *   **Amazon Seller Central:** A separate ecosystem of marketplace sales data, FBA fees, referral fees, Amazon Advertising costs, and customer reviews.
    *   **Digital Advertising Platforms (Google Ads, Facebook/Instagram Ads):** Crucial spend data, campaign performance metrics (impressions, clicks, CPC), but disconnected from actual sales conversions across all channels.
    *   **Cost of Goods Sold (COGS) & Inventory:** Often managed in disparate systems or even spreadsheets, making it difficult to accurately tie procurement costs to individual sales.
    *   **Shipping & Logistics:** Variable costs from multiple carriers for their D2C fulfillment, needing careful tracking.

2.  **The Labyrinth of True Profitability Calculation:**
    *   While top-line revenue per channel was visible, determining **true net profit per product, per channel (Shopify vs. Amazon), and even per marketing campaign** was a monumental task. Allocating a myriad of costs – COGS, platform-specific fees (Shopify fees, complex Amazon FBA/referral fees), nuanced advertising spend, shipping, and returns – accurately was nearly impossible with their existing tools.
    *   **Niche Pain Point:** Deciphering the "halo effect" – how much off-Amazon advertising (e.g., a Facebook Ad) influenced subsequent direct searches and purchases on Amazon – was a complete black box.

3.  **Inefficient Marketing Spend & Opaque ROI Attribution:**
    *   ArtisanGlow struggled to get a holistic, cross-channel view of their marketing funnel. Attributing sales conversions accurately when a customer's journey might span multiple touchpoints (e.g., see a Google Ad, visit the Shopify site, later purchase on Amazon) was based on guesswork.
    *   This opacity led to fears of wasted ad spend on underperforming campaigns and missed opportunities to double down on high-ROI channels.

4.  **The Tyranny of Manual Reporting:**
    *   The finance team was ensnared in a cycle of **manual, time-consuming, and error-prone reporting.** Month-end involved arduously downloading multiple CSVs, painstakingly cleaning data, and wrestling with brittle, complex spreadsheets (VLOOKUPs, SUMIFs galore!).
    *   This not only consumed valuable skilled time but also led to significant delays in delivering insights for strategic decision-making and a pervasive lack of trust in the numbers due to potential human error.

5.  **The Scalability Bottleneck:**
    *   ArtisanGlow's manual processes and spreadsheet-based analytics were clearly unsustainable with their aggressive growth trajectory. They recognized the urgent need for a robust, automated solution that could scale with their data volume and business complexity, without requiring an immediate, large investment in a dedicated data engineering team.

## 💡 The Solution: An AWS-Powered Engine for Unified Commerce Intelligence

This project implements a scalable, automated, and self-service-oriented financial analytics platform on AWS, specifically designed to address the challenges faced by ArtisanGlow. It provides a blueprint for transforming raw, multi-channel data into actionable insights.

**Core Architecture & Components:**

*   **Amazon S3 (Data Lake Foundation):** Serves as the central, scalable, and cost-effective repository for all raw and processed data. ArtisanGlow can land data exports from Shopify, Seller Central, ad platforms, and COGS systems here in various formats.
*   **AWS Glue (Intelligent ETL & Data Catalog):** The workhorse for data transformation and preparation.
    *   **ETL Jobs (PySpark):** Scripts are designed to automatically ingest data from S3, perform complex transformations (data cleansing, standardization, currency conversion if needed), join disparate datasets (e.g., sales with ad spend, sales with COGS), and implement crucial business logic for **cost allocation and multi-touch attribution (conceptually).**
    *   **Glue Data Catalog:** Acts as a central metadata repository, making data easily discoverable and usable by Redshift and other analytics services.
*   **Amazon Redshift (High-Performance Cloud Data Warehouse):** Stores the curated, analysis-ready data in a meticulously designed **star schema.** This schema is optimized for financial reporting and BI, featuring dimensions like `DimDate`, `DimProduct`, `DimChannel` (Shopify, Amazon-FBA, Amazon-MFBM), `DimCustomer` (unified where possible), `DimAdCampaign`, `DimPromotion`, and a central `FactFinancialPerformance` table. This fact table consolidates sales, all associated costs, and calculated profitability metrics at a granular level.
*   **AWS CloudFormation (Infrastructure as Code):** The entire AWS infrastructure (VPC, S3 buckets, IAM roles, Redshift cluster, Glue jobs, Secrets Manager) is defined in a comprehensive CloudFormation template. This enables:
    *   **Automated, Repeatable Deployments:** Spin up or tear down the entire environment consistently.
    *   **Version Control & Auditing:** Track infrastructure changes alongside application code.
    *   **Scalability & Maintainability:** Easily update and manage the infrastructure as needs evolve.
*   **AWS Secrets Manager:** Securely manages sensitive credentials like the Redshift master password, integrating seamlessly with CloudFormation and accessible by the Glue ETL jobs.
*   **Robust Networking (VPC):** A custom Amazon VPC with public and private subnets, NAT Gateways, and an S3 gateway endpoint ensures secure and efficient data flow.

**Key Transformations & Business Logic (Conceptual - Handled by Glue):**

*   **Unified Customer View:** Logic to attempt to identify and merge customer records across Shopify and Amazon where possible.
*   **Fee Calculation Engine:** Applying complex fee structures from Amazon (referral fees, FBA fees, storage fees) and Shopify (transaction fees).
*   **COGS Allocation:** Joining sales data with product cost data based on sale date to ensure accurate COGS per transaction.
*   **Ad Spend Attribution:** Implementing attribution models (e.g., last-click, multi-touch - conceptually) to allocate ad spend from various platforms to sales transactions.
*   **Currency Conversion:** Standardizing all monetary values to a single currency if sources use different ones.

## ✨ Empowering ArtisanGlow: The Tangible Benefits

By implementing this platform, ArtisanGlow can achieve:

*   **A Single Source of Truth:** Consolidated financial and operational data for reliable reporting and analysis.
*   **Clear Profitability Insights:** Understand true net profitability by product, channel, campaign, and customer segment.
*   **Optimized Marketing ROI:** Make data-driven decisions on ad spend allocation by accurately measuring cross-channel campaign effectiveness.
*   **Automated & Efficient Reporting:** Free up the finance team for higher-value analysis instead of manual data wrangling.
*   **Scalable Foundation:** A platform that grows with their business, enabling future capabilities like demand forecasting, customer lifetime value (CLV) analysis, and advanced anomaly detection.
*   **Enhanced Data Governance:** Improved data quality, consistency, and security.

## 🎯 Why This Project Matters for an Amazon BIE Role

This project is designed to showcase the qualities and skills highly valued in a Business Intelligence Engineer at Amazon:

*   **Customer Obsession:** It directly addresses and solves complex, real-world pain points for a growing e-commerce business (a typical Amazon customer/seller).
*   **Ownership & End-to-End Thinking:** Demonstrates the ability to architect and conceptualize a complete data-to-insights pipeline, from raw data ingestion to enabling sophisticated BI.
*   **Bias for Action & Automation:** Emphasizes automating manual, error-prone processes and building for efficiency and scale.
*   **Dive Deep:** Requires a deep understanding of intricate business logic (multi-channel cost allocation, fee structures, marketing attribution) and the ability to translate these into robust data models and ETL processes.
*   **Technical Prowess:** Leverages a suite of core AWS data services (S3, Glue, Redshift), Infrastructure as Code (CloudFormation), security best practices (IAM, Secrets Manager, VPC), and data warehousing principles (star schema).
*   **Frugality (Smart Scalability):** By building on AWS's flexible and pay-as-you-go infrastructure, the solution is cost-effective and avoids large upfront investments, scaling as the business grows.
*   **Deliver Results:** The ultimate aim is to empower the business with actionable intelligence that drives improved profitability, operational efficiency, and strategic growth.

This platform is more than just a technical exercise; it's a blueprint for how businesses can leverage AWS to achieve data-driven decision-making and unlock their full potential in a competitive multi-channel landscape.

## 🛠️ Technology Stack

*   **Data Lake:** Amazon S3
*   **ETL:** AWS Glue (PySpark)
*   **Data Warehouse:** Amazon Redshift
*   **Infrastructure as Code:** AWS CloudFormation
*   **Secrets Management:** AWS Secrets Manager
*   **Networking:** Amazon VPC (Virtual Private Cloud)
*   **Identity & Access Management:** AWS IAM
*   **Placeholder for BI/Visualization:** Amazon QuickSight / Tableau (conceptual)

## 📂 Project Structure

```
aws_finance_analytics_poc/
├── data/
│   ├── raw/                # Raw data extracts (e.g., transactions.csv, marketing_spend.csv, cogs.csv)
│   │   ├── transactions.csv  # Combined sales from Shopify, Amazon
│   │   ├── marketing_spend.csv # Spend from Google Ads, Facebook Ads, Amazon Ads
│   │   └── cogs.csv          # Cost of goods sold per SKU
│   └── processed/          # Processed data (e.g., Parquet files for Redshift staging)
│       └── .gitkeep
├── docs/
│   └── .gitkeep            # Additional documentation (e.g., detailed data model, ETL logic deep-dive)
├── etl/
│   └── glue_etl_job.py     # PySpark script for AWS Glue ETL job
├── infra/
│   └── cloudformation_template.yaml # AWS CloudFormation template for infrastructure
├── sql/
│   ├── ddl/                # Data Definition Language scripts for Redshift
│   │   ├── create_dimensions.sql
│   │   └── create_facts.sql
│   └── dml/                # Data Manipulation Language scripts (sample queries)
│       └── sample_queries.sql
├── .gitignore
├── LICENSE.md
└── README.md
```

## 📊 Data Model (Conceptual Star Schema for Redshift)

*   **Fact Table:**
    *   `FactFinancialPerformance`: Contains granular transaction-level or daily summary data with foreign keys to dimension tables and key measures (Revenue, Discounts, ShippingRevenue, COGS, AmazonFees, ShopifyFees, AdSpend, Returns, NetProfit, etc.).
*   **Dimension Tables:**
    *   `DimDate`: Date attributes (Day, Month, Quarter, Year, DayofWeek, etc.).
    *   `DimProduct`: Product details (SKU, Name, Category, Brand, Supplier).
    *   `DimChannel`: Sales channel (e.g., 'Shopify Web', 'Amazon FBA', 'Amazon FBM').
    *   `DimCustomer`: Customer attributes (CustomerID, Segment, Location - PII considerations apply).
    *   `DimAdCampaign`: Marketing campaign details (CampaignID, CampaignName, SourcePlatform (Google/Facebook/Amazon Ads), CampaignType).
    *   `DimPromotion`: Discount codes or promotions applied.

## ⚙️ Setup and Deployment (Conceptual Overview)

1.  **Prerequisites:** AWS Account, AWS CLI configured, necessary IAM permissions for CloudFormation deployment.
2.  **Customize Parameters:** Review and update parameters in `infra/cloudformation_template.yaml` (e.g., `ProjectPrefix`, VPC CIDRs).
3.  **Upload Glue Script to S3:** Place the `etl/glue_etl_job.py` into the S3 bucket that will be created by CloudFormation for Glue scripts.
4.  **Deploy CloudFormation Stack:**
    ```bash
    aws cloudformation deploy \
        --template-file infra/cloudformation_template.yaml \
        --stack-name <your-stack-name> \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --parameter-overrides ProjectPrefix=<your-prefix> RedshiftMasterUsername=<your-user> # Add other params as needed
    ```
5.  **Prepare Raw Data:** Upload sample CSV files (or your actual data) to the 'raw' S3 bucket created by the stack.
6.  **Run AWS Glue ETL Job:** Trigger the `*-Financial-ETL-Job` from the AWS Glue console or via the AWS CLI/SDK.
7.  **Connect BI Tool:** Connect your preferred BI tool (e.g., Amazon QuickSight, Tableau) to the Amazon Redshift cluster using the endpoint and credentials (master user from parameters, password from Secrets Manager).

## 🚀 Running the PoC & Exploring Data

1.  Once the Glue job completes successfully, your Redshift data warehouse will be populated.
2.  Use the sample queries in `sql/dml/sample_queries.sql` (via a Redshift query editor) to explore the data and validate the ETL process.
3.  Build dashboards in your BI tool to visualize key performance indicators (KPIs) like:
    *   Channel-wise Profitability.
    *   Product Contribution Margin.
    *   Marketing Campaign ROI.
    *   Sales Trends (Daily, Monthly, Quarterly).

## ✨ Key Features & Strengths of this Approach

*   **Automation:** End-to-end automation from infrastructure deployment to ETL.
*   **Scalability:** AWS services scale seamlessly with data volume and processing needs.
*   **Cost-Effectiveness:** Pay-as-you-go model, optimized for growing businesses.
*   **Data-Driven Culture:** Empowers teams with self-service access to reliable, unified data.
*   **Modularity:** Components can be enhanced or replaced independently.
*   **Security:** Utilizes IAM, Secrets Manager, and VPC for a secure environment.

## 🔮 Future Enhancements (Roadmap)

*   **Event-Driven ETL:** Transition to S3 event-triggered Glue jobs for near real-time data processing.
*   **API-based Data Ingestion:** Replace CSV uploads with direct API connections to Shopify, Amazon SP-API, Google Ads API, Facebook Marketing API for more robust and timely data acquisition (using services like AWS AppFlow or custom Lambda functions).
*   **Advanced Analytics:** Incorporate machine learning (e.g., Amazon SageMaker) for demand forecasting, customer segmentation, anomaly detection in spending.
*   **Data Quality Monitoring:** Implement automated data quality checks within the Glue ETL process or using services like AWS Deequ.
*   **CI/CD Pipeline:** Set up a CI/CD pipeline (e.g., AWS CodePipeline, GitHub Actions) for automated testing and deployment of CloudFormation and Glue script changes.
*   **Granular Access Control in Redshift:** Define specific user roles and permissions within Redshift for different teams.
*   **Interactive Dashboards:** Develop pre-built QuickSight dashboards for common financial reports.

## 🤝 Contributing

Contributions, ideas, and feedback are welcome! Please open an issue or submit a pull request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
