- join a room
  - we see the timers of all people present
  - host/invitees can choose or not to share their current intention, defaults to no
  - when creating a room, there's a simple link that the host/invitees can share to let people join, it likely opens sharepoint.pucoti.com then pucoti:// or something similar
    - the url contains the id of the room, then the joining is handled on the app client side
  - rooms are limited to 20 people
  - there is a 5 per minute rate-limit on the join endpoint
  - if the host leaves the room with other people in it, the next person becomes the host
    - how do we know when someone leaves the room? no polling for 10 minutes
      - when the host polls, we update a leader_last_polled_at field on the room, if it exceeds ten minute, we switch hosts
      - if the host leaves manually (e.g., clicks on "Leave" in the UI), we switch hosts immediately,

- create a room
  - the host can choose "one timer to rule them all" option:
    - the timer is shared for all participants
    - the host sets the intention that's shown for all participants
    - if the host leaves the room in this mode, the room is removed
  - there is a 10 per hour rate-limit on the create room endpoint
  - the room ids should be short, generate automatically, easier very short but not memorable (google meet) or list of 3-4 random words


- auth/authz
   - link-based auth (key/token in URL)
   - on room creation, host gets a special token that they can use to do administrative actions
    - this is stored on the client and is valid for as long as the room exists

- intention sharing
  - A string, at most 255 chars

- we use sqlite for storage
- clients poll the room every 10s, they will update the timers on their side, and sync after a poll
