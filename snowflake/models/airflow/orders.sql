{{
    config(
        materialized='table',
        alias='orders_by_status'
    )
}}

-- return the year, order status and total order for each ombination of year and order status
with pre_orders as (
    select 
        YEAR(o.orderDate) AS year,
        status,
        SUM(odt.quantityOrdered * odt.priceEach) AS total
        from 
            {{ source('snowflake_staging', 'orders') }} o 
        inner join
            {{ source('snowflake_staging', 'orderdetails') }} odt
        group by 
            1,2
        order by 1
)

select 
    *
from 
    pre_orders