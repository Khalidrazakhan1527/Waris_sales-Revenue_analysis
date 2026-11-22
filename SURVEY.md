# Dashboard evaluation questionnaire

Recruit approximately 40–50 volunteers with sales or analytics knowledge. Give each volunteer equivalent tasks using the workbook/CSV and the interactive dashboard. Alternate which tool they use first to reduce order effects. Example tasks include identifying the leading region by revenue, finding the category with the weakest margin, and comparing revenue in two consecutive years. Use equivalent task variants across tools to reduce recall. Then administer the questionnaire below.

Explain that participation is voluntary, responses are confidential and used for academic purposes, and participants can stop at any time. Collect only anonymous scores in the response template.

For every statement, choose one answer: 1 Strongly disagree, 2 Disagree, 3 Neutral, 4 Agree, 5 Strongly agree.

| CSV field | Statement |
| --- | --- |
| speed_1 | I identified the required KPIs faster in the dashboard than in the spreadsheet. |
| speed_2 | I compared performance across periods faster in the dashboard than in the spreadsheet. |
| quality_1 | The dashboard made it easier to identify weak performance than the spreadsheet did. |
| quality_2 | I could justify my recommended decision better with the dashboard than with the spreadsheet. |
| usefulness_1 | The dashboard would help me monitor sales performance. |
| usefulness_2 | The dashboard would help me identify opportunities to improve profitability. |
| ease_1 | The dashboard filters were easy to use. |
| ease_2 | The dashboard charts and KPI labels were easy to understand. |

Enter one response per row in `survey_responses.csv`. The analysis excludes rows with missing or invalid items and reports the number excluded. It reports item means and sample standard deviations, plus separate usefulness and ease composites. For H03, average the four speed and quality items per participant, calculate Cronbach’s alpha for those four items, and test the composite against 3 with a one-sided one-sample t-test. Report the result as perceived improvement among respondents. To make a separate claim about measured speed or accuracy, record task times and correctness under both tools and analyse the paired measures separately.
