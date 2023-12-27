-- INSERT INTO account (id, account_number, user_id, account_type, balance) VALUES 
--   ('4489294367', '', '', '', '2000')
  UPDATE account SET balance = balance + 2000 WHERE id = 4489294367;
