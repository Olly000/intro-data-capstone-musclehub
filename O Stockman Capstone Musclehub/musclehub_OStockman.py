
# coding: utf-8

# # Capstone Project 1: MuscleHub AB Test

# ## Step 1: Get started with SQL

# Like most businesses, Janet keeps her data in a SQL database.  Normally, you'd download the data from her database to a csv file, and then load it into a Jupyter Notebook using Pandas.
# 
# For this project, you'll have to access SQL in a slightly different way.  You'll be using a special Codecademy library that lets you type SQL queries directly into this Jupyter notebook.  You'll have pass each SQL query as an argument to a function called `sql_query`.  Each query will return a Pandas DataFrame.  Here's an example:

# In[30]:


# This import only needs to happen once, at the beginning of the notebook
from codecademySQL import sql_query as sqlq


# In[31]:


# Here's an example of a query that just displays some data
sqlq('''
SELECT *
FROM visits
LIMIT 5
''')


# In[32]:


# Here's an example where we save the data to a DataFrame
df = sqlq('''
SELECT *
FROM applications
LIMIT 5
''')


# ## Step 2: Get your dataset

# Let's get started!
# 
# Janet of MuscleHub has a SQLite database, which contains several tables that will be helpful to you in this investigation:
# - `visits` contains information about potential gym customers who have visited MuscleHub
# - `fitness_tests` contains information about potential customers in "Group A", who were given a fitness test
# - `applications` contains information about any potential customers (both "Group A" and "Group B") who filled out an application.  Not everyone in `visits` will have filled out an application.
# - `purchases` contains information about customers who purchased a membership to MuscleHub.
# 
# Use the space below to examine each table.

# In[33]:


# Examine visits here
dfv = sqlq('''
SELECT * FROM visits
LIMIT 5''')
visitors = sqlq('''
SELECT COUNT (*) FROM visits''')
test_visitors = sqlq('''
SELECT COUNT (*) FROM visits
WHERE visit_date >= "7-1-17"''')
print dfv
print visitors
print test_visitors


# In[34]:


# Examine fitness_tests here
dfft = sqlq('''
SELECT * FROM fitness_tests
LIMIT 5''')
print dfft


# In[35]:


# Examine applications here
dfa = sqlq('''
SELECT * FROM applications
LIMIT 5''')
print dfa


# In[36]:


# Examine purchases here
dfp = sqlq('''
SELECT * FROM purchases
LIMIT 5''')
print dfp
print dfp.purchase_date.unique()


# We'd like to download a giant DataFrame containing all of this data.  You'll need to write a query that does the following things:
# 
# 1. Not all visits in  `visits` occurred during the A/B test.  You'll only want to pull data where `visit_date` is on or after `7-1-17`.
# 
# 2. You'll want to perform a series of `LEFT JOIN` commands to combine the four tables that we care about.  You'll need to perform the joins on `first_name`, `last_name`, and `email`.  Pull the following columns:
# 
# 
# - `visits.first_name`
# - `visits.last_name`
# - `visits.gender`
# - `visits.email`
# - `visits.visit_date`
# - `fitness_tests.fitness_test_date`
# - `applications.application_date`
# - `purchases.purchase_date`
# 
# Save the result of this query to a variable called `df`.
# 
# Hint: your result should have 5004 rows.  Does it?

# In[37]:


#create dataframe df containing all the information from the four original tables:
df = sqlq('''
SELECT visits.first_name, 
visits.last_name, 
visits.gender, 
visits.email, 
visits.visit_date, 
fitness_tests.fitness_test_date, 
applications.application_date, 
purchases.purchase_date

FROM visits
LEFT JOIN fitness_tests
ON visits.email = fitness_tests.email 
AND visits.first_name = fitness_tests.first_name
AND visits.last_name = fitness_tests.last_name

LEFT JOIN applications
ON visits.email = applications.email
AND visits.first_name = applications.first_name
AND visits.last_name = applications.last_name

LEFT JOIN purchases
ON visits.email = purchases.email
AND visits.first_name = purchases.first_name
AND visits.last_name = purchases.last_name

WHERE visits.visit_date >= '7-1-17'

''')

print df


# ## Step 3: Investigate the A and B groups

# We have some data to work with! Import the following modules so that we can start doing analysis:
# - `import pandas as pd`
# - `from matplotlib import pyplot as plt`

# In[38]:


import pandas as pd
from matplotlib import pyplot as plt



# We're going to add some columns to `df` to help us with our analysis.
# 
# Start by adding a column called `ab_test_group`.  It should be `A` if `fitness_test_date` is not `None`, and `B` if `fitness_test_date` is `None`.

# In[39]:



df['ab_test_group'] = df.fitness_test_date.apply(lambda x: 'A' if x != None else 'B')
print df


# Let's do a quick sanity check that Janet split her visitors such that about half are in A and half are in B.
# 
# Start by using `groupby` to count how many users are in each `ab_test_group`.  Save the results to `ab_counts`.

# In[40]:


ab_counts = df.groupby('ab_test_group').last_name.count()
print ab_counts


# We'll want to include this information in our presentation.  Let's create a pie cart using `plt.pie`.  Make sure to include:
# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[41]:


plt.pie(ab_counts, autopct = '%0.2f%%')
plt.axis('equal')
plt.legend(['A','B'])
plt.savefig('ab_test_pie_chart.png')
plt.show()


# ## Step 4: Who picks up an application?

# Recall that the sign-up process for MuscleHub has several steps:
# 1. Take a fitness test with a personal trainer (only Group A)
# 2. Fill out an application for the gym
# 3. Send in their payment for their first month's membership
# 
# Let's examine how many people make it to Step 2, filling out an application.
# 
# Start by creating a new column in `df` called `is_application` which is `Application` if `application_date` is not `None` and `No Application`, otherwise.

# In[42]:


df['is_application'] = df.application_date.apply(lambda x: 'Application' if x != None else 'No Application')
print df.head()


# Now, using `groupby`, count how many people from Group A and Group B either do or don't pick up an application.  You'll want to group by `ab_test_group` and `is_application`.  Save this new DataFrame as `app_counts`

# In[43]:


app_counts = df.groupby(['ab_test_group','is_application']).last_name.count().reset_index()
print app_counts
print type(app_counts)


# We're going to want to calculate the percent of people in each group who complete an application.  It's going to be much easier to do this if we pivot `app_counts` such that:
# - The `index` is `ab_test_group`
# - The `columns` are `is_application`
# Perform this pivot and save it to the variable `app_pivot`.  Remember to call `reset_index()` at the end of the pivot!

# In[44]:


app_pivot = app_counts.pivot(columns = 'is_application',
            index = 'ab_test_group',
            values = 'last_name').reset_index()
print app_pivot


# Define a new column called `Total`, which is the sum of `Application` and `No Application`.

# In[45]:


app_pivot['Total'] = app_pivot['Application']+app_pivot['No Application']

print app_pivot


# Calculate another column called `Percent with Application`, which is equal to `Application` divided by `Total`.

# In[46]:


app_pivot['Percent_with_Application'] = (app_pivot['Application']/app_pivot['Total'])*100
print app_pivot


# It looks like more people from Group B turned in an application.  Why might that be?
# 
# We need to know if this difference is statistically significant.
# 
# Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[47]:


#this requires a chi square test to assess
from scipy.stats import chi2_contingency

contin_table = [[250,325],
                [2254,2175]]
chi2, pvalue, dof, expected = chi2_contingency(contin_table)
print pvalue
"""pvalue is well below 0.05 therefore the null hypothesis can be rejected - 
 a signficantly larger number of people applied where no fitness test was administered"""


# ## Step 4: Who purchases a membership?

# Of those who picked up an application, how many purchased a membership?
# 
# Let's begin by adding a column to `df` called `is_member` which is `Member` if `purchase_date` is not `None`, and `Not Member` otherwise.

# In[48]:


df['is_member'] = df.purchase_date.apply(lambda x: 'Not Member' if x == None else 'Member')
print df.head()



# Now, let's create a DataFrame called `just_apps` the contains only people who picked up an application.

# In[49]:


just_apps = df[df['is_application'] == 'Application'].reset_index()
print just_apps.head()


# Great! Now, let's do a `groupby` to find out how many people in `just_apps` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `member_pivot`.

# In[50]:


members_by_group = just_apps.groupby(['ab_test_group', 'is_member']).last_name.count().reset_index()
member_pivot = members_by_group.pivot(columns = 'is_member',
                                     index = 'ab_test_group',
                                     values = 'last_name').reset_index()

member_pivot['Total'] = member_pivot['Member']+ member_pivot['Not Member']
member_pivot['Percent Purchase'] = (member_pivot['Member']/member_pivot['Total'])*100
print member_pivot


# It looks like people who took the fitness test were more likely to purchase a membership **if** they picked up an application.  Why might that be?
# 
# Just like before, we need to know if this difference is statistically significant.  Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[51]:


from scipy.stats import chi2_contingency

cont_table = [[200,250],
             [50,75]]
chi2, pval, dof, expected = chi2_contingency(cont_table)
print pval
"""The pvalue for this test is over 0.05 therefore the null hypothesis
cannot be rejected.  We must conclude that there was no difference in the
proportion of those becoming members with or without a fitness test for the 
sub-group of visitors that picked up an application"""


# Previously, we looked at what percent of people **who picked up applications** purchased memberships.  What we really care about is what percentage of **all visitors** purchased memberships.  Return to `df` and do a `groupby` to find out how many people in `df` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `final_member_pivot`.

# In[52]:


all_members_by_group = df.groupby(['ab_test_group', 'is_member']).last_name.count().reset_index()
final_member_pivot = all_members_by_group.pivot(columns = 'is_member',
                                     index = 'ab_test_group',
                                     values = 'last_name').reset_index()

final_member_pivot['Total'] = final_member_pivot['Member']+ final_member_pivot['Not Member']
final_member_pivot['Percent Purchase'] = (final_member_pivot['Member']/final_member_pivot['Total'])*100
print final_member_pivot


# Previously, when we only considered people who had **already picked up an application**, we saw that there was no significant difference in membership between Group A and Group B.
# 
# Now, when we consider all people who **visit MuscleHub**, we see that there might be a significant different in memberships between Group A and Group B.  Perform a significance test and check.

# In[53]:


all_cont_table = [[200,250],
             [2304,2250]]
chi2, pval_all, dof, expected = chi2_contingency(all_cont_table)
print pval_all
"""pval is below 0.05 so a significant difference between A and B can be supported by the data
those who took part in the fitness test were less likely, overall, to become members"""


# ## Step 5: Summarize the acquisition funel with a chart

# We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each state of the process:
# - Percent of visitors who apply
# - Percent of applicants who purchase a membership
# - Percent of visitors who purchase a membership
# 
# Create one plot for **each** of the three sets of percentages that you calculated in `app_pivot`, `member_pivot` and `final_member_pivot`.  Each plot should:
# - Label the two bars as `Fitness Test` and `No Fitness Test`
# - Make sure that the y-axis ticks are expressed as percents (i.e., `5%`)
# - Have a title

# In[124]:


#create a new figure for the three plots to be placed in:
plt.figure(figsize = (18,6))

#define first subplot
plt.subplot(1,3,1)
plt.bar(app_pivot.ab_test_group, app_pivot.Percent_with_Application)
plt.title('Percentage of Visitors That Applied to Join')
ax = plt.subplot(1,3,1)
ax.set_xticks(range(len(app_pivot.ab_test_group)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks(range(0,16,2))
ax.set_yticklabels(['0%','2%','4%','6%','8%','10%','12%','14%'])
plt.ylabel('% of visitors that applied', rotation = 90)
plt.savefig('mh_plots_row.png')

#define second subplot
plt.subplot(1,3,2)
plt.bar(member_pivot.ab_test_group, member_pivot['Percent Purchase'])
plt.title('Percentage of Applicants That Purchased a Membership')
ax2 = plt.subplot(1,3,2) 
ax2.set_xticks(range(len(member_pivot.ab_test_group)))
ax2.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax2.set_yticks(range(0,90,10))
ax2.set_yticklabels(['0%','10%','20%','30%','40%','50%','60%','70%','80%'])
plt.ylabel('% of applicants that joined', rotation = 90)
plt.savefig('mh_plots_row.png')

#define third subplot
plt.subplot(1,3,3)
plt.bar(final_member_pivot.ab_test_group, final_member_pivot['Percent Purchase'])
plt.title('Percentage of Visitors That Purchased a Membership')
ax3 = plt.subplot(1,3,3) 
ax3.set_xticks(range(len(final_member_pivot.ab_test_group)))
ax3.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax3.set_yticks(range(0,12,2))
ax3.set_yticklabels(['0%','2%','4%','6%','8%','10%'])
plt.ylabel('% of visitors that joined', rotation = 90)

#output resulting figure
plt.savefig('mh_plots_row.png')


# In[120]:



