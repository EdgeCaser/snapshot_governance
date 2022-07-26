#declarations

from datetime import datetime
from datetime import date
from subgrounds.subgraph import SyntheticField
from subgrounds.subgrounds import Subgrounds
import pandas as pd
sg = Subgrounds()
snapshot = sg.load_api('https://hub.snapshot.org/graphql')

global file
file = input('Enter output filepath')

snapshot.Proposal.datetime = SyntheticField(
  lambda timestamp: str(datetime.fromtimestamp(timestamp)),
  SyntheticField.STRING,
  snapshot.Proposal.end,
)

spacename = input('spacename plz?')
proposals = snapshot.Query.proposals(
  orderBy='created',
  orderDirection='desc',
  first=10000,
  where=[
    snapshot.Proposal.space == spacename,
    snapshot.Proposal.state == 'closed'
  ]
)

proposals_snapshots = sg.query_df([
    proposals.title,
    proposals.id,
    proposals.body,
    proposals.scores,
    proposals.scores_total
])

proposals_choices = sg.query(proposals.choices)

proposals_choices = pd.DataFrame(proposals_choices)

olympus_governance_view = pd.concat([proposals_snapshots,proposals_choices], axis=1)

path =file+'/'+spacename+'_proposals_table_'+str(date.today().strftime("%b-%d-%Y"))+'_'+str(len(olympus_governance_view))+'_proposals.csv'
olympus_governance_view.to_csv(path, index = False)

total_proposals = len(olympus_governance_view)

proposal_id = olympus_governance_view.iloc[0,1]

vote_tracker = snapshot.Query.votes(
orderBy = 'created',
orderDirection='desc',
first=10000,
where=[
  snapshot.Vote.proposal == proposal_id
]
)

voting_snapshots_list = sg.query_df([
    vote_tracker.id,
    vote_tracker.voter,
    vote_tracker.created,
    vote_tracker.choice,
    vote_tracker.vp
])

voting_snapshots_list['Proposal'] = proposal_id

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

    x=x+1

path =file+'/'+spacename+'_voting_snapshots_list_'+str(date.today().strftime("%b-%d-%Y"))+'_'+str(len(olympus_governance_view))+'.csv'
voting_snapshots_list.to_csv(path, index = False)

print('Finished')