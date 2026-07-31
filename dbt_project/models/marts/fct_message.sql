with stg as (select * from {{ ref('stg_telegram_messages') }}),
channels as (select * from {{ ref('dim_channels') }}),
dates as (select * from {{ ref('dim_dates') }})
select
    stg.message_id,
    channels.channel_key,
    dates.date_key,
    stg.message_text,
    stg.message_length,
    stg.views,
    stg.forwards,
    stg.has_image,
    stg.image_path
from stg
left join channels on stg.channel_name = channels.channel_name
left join dates on stg.message_date::date = dates.full_date
