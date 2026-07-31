with source as (
    select * from raw.telegram_messages
),
renamed as (
    select
        message_id,
        channel_name,
        message_date::timestamp as message_date,
        message_text,
        has_media,
        views,
        forwards,
        image_path,
        length(message_text) as message_length
    from source
    where message_text is not null and trim(message_text) != ''
)
select * from renamed
