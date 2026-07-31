with channels as (
    select distinct channel_name from {{ ref('stg_telegram_messages') }}
)
select
    row_number() over (order by channel_name) as channel_key,
    channel_name,
    -- You can enrich with category from a mapping file later
    'Unknown' as channel_type,
    min(message_date) as first_post_date,
    max(message_date) as last_post_date,
    count(*) as total_posts,
    avg(views) as avg_views
from channels
left join {{ ref('stg_telegram_messages') }} using (channel_name)
group by channel_name
