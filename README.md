# -1Chan Message Board



----------------------------------
## 1. Problem Description
----------------------------------
We will be designing a message board. The message board will organize community Threads under Topics. Users will be able to register using a unique user_name and password. Users can create threads under existing topics, add posts to existing threads, and add comments to existing posts. 

The front end will display pages to help users navigate through the topics, threads, and posts. Users will have their own home page, where they can personalize a profile. A user’s profile will be linked to all of their existing posts. Likewise, any post will be linked to a user’s profile page. 


----------------------------------
## 2. Proposed system
----------------------------------
Here are the necessary Entities within this system:
•       Topic – (topic_id (PK), topic_title, topic_image)

•       Thread – (thread_id (PK), topic_id (FK), user_name (FK), thread_title, thread_image,      thread_creation_time)

•       Post – (post_id (PK), user_name  (FK), post_title, post_text, post_creation_time, posts_likes, posts_dislikes)

•    Comment - (comment_id (PK), user_name (FK), post_id(FK), comment_text,      comment_creation_time, comment_likes, comment_dislikes)

•       User – (user_name (PK), password, profile_text, user_image, roles, vote_ratio)

 
----------------------------------
## 3. System Specification (proposed)
----------------------------------
Hardware Requirements:
Computer - to be able to run and access the site
Server - Hosting the website and database server
Database Server - Storing all relevant information from the users and other entities above
Software Requirements: 
Python, we chose this language because it is compatible with our chosen backend and frontend languages and we all have experience with it.
PostgreSQL as one of us has experience and it is an established, detailed database system that allows for the scalability and security that we need. 
Django can handle routing and frontend design that would be fairly easy to implement and learn shorthand. 
SQLAlchemy and Psycopg2 library because we are using Python to code and interacting with PostgreSQL databases. Essentially our accessor to databases. 
