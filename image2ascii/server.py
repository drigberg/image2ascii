import typing
import uuid

from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room


app = Flask("image2ascii")
socketio = SocketIO(app)


@app.route('/health', method="GET")
def getHealth() -> typing.Mapping[str, str]:
    return {"ok": "ok"}


class Room:
    def __init__(self):
        self.room_id = uuid.uuid4()
        self.members = []

    def join(self, username: str) -> None:
        assert len(self.members) < 2
        self.members.append(username)

    def leave(self, username: str) -> None:
        self.members = [
            member for member in self.members
            if member != username]


class Rooms:
    def __init__(self):
        self.rooms = []

    def create_room(self):
        room = Room()
        self.rooms.append(room)
        return room

    def find_room_by_id(self, room_id: str) -> typing.Optional[Room]:
        matches = [
            room for room in self.rooms
            if room.room_id == room_id]
        assert len(matches) < 2, f"Found multiple rooms with id {room_id}"
        return matches[0] if matches else None


@app.route('/health', method="GET")
def createRoom() -> typing.Mapping[str, str]:
    room = Rooms.create_room()
    return {"room_id": room.room_id}


@socketio.on('join')
def on_join(data):
    username = data['username']
    room_id = data['room_id']
    join_room(room_id)
    emit('user_joined', username + ' has entered the room.', room=room_id)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room_id = data['room_id']
    leave_room(room_id)
    emit('user_left', username + ' has left the room.', room=room_id)


if __name__ == '__main__':
    socketio.run(app)
