#!/usr/bin/env python
# coding: utf-8

# In[49]:


from datetime import datetime
from datetime import date
from subgrounds.subgraph import SyntheticField, FieldPath
from subgrounds.subgrounds import Subgrounds
import math
import pandas as pd


# In[50]:


sg = Subgrounds()
snapshot = sg.load_api('https://hub.snapshot.org/graphql')


# global file
# file = input('Selet a folder') ##enter your file path here - the file is in the repo "summary_stats.csv".
# ##file

# In[51]:


snapshot.Proposal.datetime = SyntheticField(
  lambda timestamp: str(datetime.fromtimestamp(timestamp)),
  SyntheticField.STRING,
  snapshot.Proposal.end,
)


# In[52]:


spacename = input('spacename plz?')
proposals = snapshot.Query.proposals(
  orderBy='created',
  orderDirection='desc',
  first=10000,
  where=[
    snapshot.Proposal.space == spacename, ##'fuse.eth',
    snapshot.Proposal.state == 'closed'
    ##snapshot.Proposal.title == 'OIP-18: Reward rate framework and reduction',
  ]
)


# In[53]:


proposals_snapshots = sg.query_df([
    proposals.title,
    proposals.id,
    proposals.body,
    proposals.scores,
    proposals.scores_total
])


# In[54]:


proposals_choices = sg.query(proposals.choices)


# In[55]:


proposals_choices = pd.DataFrame(proposals_choices)
##proposals_choices = pd.DataFrame(proposals_choices, columns = ['option_1', 'option_2', 'option_3', 'option_4', 'option_5','option_6','option_7','option_8','option_9','option_10','option_11','option_12','option_13','option_14','option_15','option_16','option_17','option_18','option_19','option_20','option_21','option_22'])


# In[56]:


olympus_governance_view = pd.concat([proposals_snapshots,proposals_choices], axis=1)


# In[57]:


##let's view the output just to make sure
olympus_governance_view


# In[58]:


path =file+'/'+spacename+'_proposals_table_'+str(date.today().strftime("%b-%d-%Y"))+'_'+str(len(olympus_governance_view))+'_proposals.csv'
olympus_governance_view.to_csv(path, index = False)


# In[59]:


total_proposals = len(olympus_governance_view)
total_proposals


# In[60]:


proposal_id = olympus_governance_view.iloc[0,1]


# In[61]:


print(proposal_id)


# In[62]:



vote_tracker = snapshot.Query.votes(
orderBy = 'created',
orderDirection='desc',
first=10000,
where=[
  snapshot.Vote.proposal == proposal_id
]
)


# In[63]:


voting_snapshots_list = sg.query_df([
    vote_tracker.id,
    vote_tracker.voter,
    vote_tracker.created,
    vote_tracker.choice,
    vote_tracker.vp
])


# In[64]:


voting_snapshots_list


# In[65]:


voting_snapshots_list['Proposal'] = proposal_id
voting_snapshots_list


# In[66]:


x=0
while x <total_proposals:
##print(olympus_governance_view.iloc[2,1])
    proposal_id = olympus_governance_view.iloc[x,1]

    vote_tracker = snapshot.Query.votes(
    orderBy = 'created',
    orderDirection='desc',
    first=10000,
    where=[
      snapshot.Vote.proposal == proposal_id
    ]
    )
    voting_snapshots = sg.query_df([
    vote_tracker.id,
    vote_tracker.voter,
    vote_tracker.created,
    vote_tracker.choice,
    vote_tracker.vp
    ])

    voting_snapshots['Proposal'] = proposal_id
    voting_snapshots_list=pd.concat([voting_snapshots_list, voting_snapshots])
    ##voting_snapshots['Proposal'] = proposal_id

#    pd.concat([voting_snapshots_list, voting_snapshots])
    x=x+1


# In[67]:


len(voting_snapshots_list)


# In[68]:


path =file+'/'+spacename+'_voting_snapshots_list_'+str(date.today().strftime("%b-%d-%Y"))+'_'+str(len(olympus_governance_view))+'.csv'
voting_snapshots_list.to_csv(path, index = False)


# In[69]:


print("finished")

