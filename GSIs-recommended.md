GSI1: upload dashboard query

Use this for:

list records for an upload
sort/filter by severity and leakage

Keys:

gsi1pk
gsi1sk

Pattern:

gsi1pk = UPLOAD#<upload_id>
gsi1sk = SEVERITY#<severity>#LEAKAGE#<zero_padded_amount>#RECORD#<record_id>

This helps with dashboard listing.

GSI2: flagged records query

Use this for:

quickly fetch all flagged records
optionally across uploads

Keys:

gsi2pk
gsi2sk

Pattern:

gsi2pk = FLAGGED#YES or FLAGGED#NO
gsi2sk = UPLOAD#<upload_id>#SEVERITY#<severity>#RECORD#<record_id>

For MVP, GSI1 may be enough. GSI2 is a stretch but nice.

Recommended query usage
Upload detail page: query pk = UPLOAD#u_001
Records list: query GSI1 with gsi1pk = UPLOAD#u_001
Record detail: get pk = UPLOAD#u_001 + sk = RECORD#r_001
Analysis detail: query pk = UPLOAD#u_001 and begins_with(sk, 'ANALYSIS#r_001#')