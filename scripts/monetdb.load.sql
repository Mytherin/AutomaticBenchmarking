
COPY INTO region   FROM '_DIR_/region.tbl'   USING DELIMITERS '|', '\n' LOCKED;
COPY INTO nation   FROM '_DIR_/nation.tbl'   USING DELIMITERS '|', '\n' LOCKED;
COPY INTO supplier FROM '_DIR_/supplier.tbl' USING DELIMITERS '|', '\n' LOCKED;
COPY INTO customer FROM '_DIR_/customer.tbl' USING DELIMITERS '|', '\n' LOCKED;
COPY INTO part     FROM '_DIR_/part.tbl'     USING DELIMITERS '|', '\n' LOCKED;
COPY INTO partsupp FROM '_DIR_/partsupp.tbl' USING DELIMITERS '|', '\n' LOCKED;
COPY INTO orders   FROM '_DIR_/orders.tbl'   USING DELIMITERS '|', '\n' LOCKED;
COPY INTO lineitem FROM '_DIR_/lineitem.tbl' USING DELIMITERS '|', '\n' LOCKED;