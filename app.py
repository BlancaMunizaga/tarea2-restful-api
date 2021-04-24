from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from base64 import b64encode
import json

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
BASE = "https://git.heroku.com/tarea2-restful-api.git"


class TrackModel(db.Model):
    __tablename__ = 'tracks'
    artist_id = db.Column(db.String(100), nullable=False)
    album_id = db.Column(db.String(100), db.ForeignKey(
        'albums.id', ondelete='CASCADE'))
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Float, nullable=False)
    times_played = db.Column(db.Integer, nullable=False)
    artist = db.Column(db.String(250), nullable=False)
    album = db.Column(db.String(250), nullable=False)
    selfs = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f"Track(artist_id = {artist_id}, name = {name})"


class AlbumModel(db.Model):
    __tablename__ = 'albums'
    artist_id = db.Column(db.String(100), db.ForeignKey(
        'artist.id', ondelete='CASCADE'))
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    artista = db.Column(db.String(250), nullable=False)
    trackes = db.Column(db.String(250), nullable=False)
    selfs = db.Column(db.String(250), nullable=False)
    tracks = db.relationship(
        'TrackModel', backref='albums', cascade="all, delete",
        lazy='dynamic')

    def __repr__(self):
        return f"Albums(artist_id = {artist_id}, name = {name}, genre = {genre})"


class ArtistModel(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    albumnes = db.Column(db.String(250), nullable=False)
    tracks = db.Column(db.String(250), nullable=False)
    selfs = db.Column(db.String(250), nullable=False)
    albums = db.relationship(
        'AlbumModel', backref='artist', cascade='all, delete',
        lazy='dynamic')

    def __repr__(self):
        return f"Artist(name = {name}, age = {age})"


artist_post_args = reqparse.RequestParser()
artist_post_args.add_argument(
    "name", type=str, help="input inválido", required=True)
artist_post_args.add_argument(
    "age", type=int, help="input inválido", required=True)

albums_post_args = reqparse.RequestParser()
albums_post_args.add_argument(
    "name", type=str, help="input inválido", required=True)
albums_post_args.add_argument(
    "genre", type=str, help="input inválido", required=True)

tracks_post_args = reqparse.RequestParser()
tracks_post_args.add_argument(
    "name", type=str, help="input inválido", required=True)
tracks_post_args.add_argument(
    "duration", type=int, help="input inválido", required=True)

resource_fields = {
    'id': fields.String,
    'name': fields.String,
    'age': fields.Integer,
    'albums': fields.String(attribute='albumnes'),
    'tracks': fields.String,
    'self': fields.String(attribute='selfs')
}

resource_albums_fields = {
    'id': fields.String,
    'artist_id': fields.String,
    'name': fields.String,
    'genre': fields.String,
    'artist': fields.String(attribute='artista'),
    'tracks': fields.String(attribute='trackes'),
    'self': fields.String(attribute='selfs')
}

resource_track_fields = {
    'id': fields.String,
    'album_id': fields.String,
    'name': fields.String,
    "duration": fields.Integer,
    "times_played": fields.Integer,
    'artist': fields.String,
    'album': fields.String,
    'self': fields.String(attribute='selfs')

}


class Artist(Resource):
    @marshal_with(resource_fields)
    def get(self):
        result = ArtistModel.query.all()
        return result, 200

    @marshal_with(resource_fields)
    def post(self):
        args = artist_post_args.parse_args()
        artist_id = b64encode(args['name'].encode()).decode('utf-8')[0:22]
        result = ArtistModel.query.filter_by(id=artist_id).first()
        if result:
            return result, 409
        albums = BASE + "/artists/" + artist_id + "/albums"
        tracks = BASE + "/artists/" + artist_id + "/tracks"
        selfs = BASE + "/artists/" + artist_id
        artist = ArtistModel(
            id=artist_id, name=args['name'], age=args['age'], albumnes=albums, tracks=tracks, selfs=selfs)
        db.session.add(artist)
        db.session.commit()
        return artist, 201


class ArtistId(Resource):
    @marshal_with(resource_fields)
    def get(self, artist_id):
        result = ArtistModel.query.filter_by(id=artist_id).first()
        if not result:
            abort(404, message="artista no encontrado")
        return result, 200

    def delete(self, artist_id):
        result = ArtistModel.query.filter_by(id=artist_id).first()
        if not result:
            abort(404, message="artista inexistente")
        db.session.delete(result)
        db.session.commit()
        return '', 204


class Albums(Resource):
    @marshal_with(resource_albums_fields)
    def get(self, artist_id):
        artist = ArtistModel.query.filter_by(id=artist_id).first()
        if not artist:
            abort(404, message="artista no encontrado")
        result = AlbumModel.query.filter_by(artist_id=artist_id).all()
        return result, 200

    @ marshal_with(resource_albums_fields)
    def post(self, artist_id):
        artist = ArtistModel.query.filter_by(id=artist_id).first()
        if not artist:
            abort(422, message="artista no existe")
        args = albums_post_args.parse_args()
        name = args['name'] + ':' + artist_id
        album_id = b64encode(name.encode()).decode('utf-8')[0:22]
        result = AlbumModel.query.filter_by(id=album_id).first()
        if result:
            return result, 409
        artista = BASE + "/artists/" + artist_id
        tracks = BASE + "/albums/" + album_id + "/tracks"
        selfs = BASE + "/albums/" + album_id
        album = AlbumModel(artist_id=artist_id, id=album_id,
                           name=args['name'], genre=args['genre'], artista=artista, trackes=tracks, selfs=selfs)
        db.session.add(album)
        db.session.commit()
        return album, 201


class AlbumsAll(Resource):
    @marshal_with(resource_albums_fields)
    def get(self):
        result = AlbumModel.query.all()
        return result, 200


class AlbumsId(Resource):
    @marshal_with(resource_albums_fields)
    def get(self, album_id):
        result = AlbumModel.query.filter_by(id=album_id).first()
        if not result:
            abort(404, message="álbum no encontrado")
        return result, 200

    def delete(self, album_id):
        result = AlbumModel.query.filter_by(id=album_id).first()
        if not result:
            abort(404, message="álbum no encontrado")
        db.session.delete(result)
        db.session.commit()
        return '', 204


class Tracks(Resource):
    @marshal_with(resource_track_fields)
    def get(self, album_id):
        album = AlbumModel.query.filter_by(id=album_id).first()
        if not album:
            abort(404, message="album no encontrado")
        result = TrackModel.query.filter_by(album_id=album_id).all()
        return result, 200

    @marshal_with(resource_track_fields)
    def post(self, album_id):
        album = AlbumModel.query.filter_by(id=album_id).first()
        if not album:
            abort(422, message="álbum no existe")
        args = tracks_post_args.parse_args()
        name = args['name'] + ':' + album_id
        track_id = b64encode(name.encode()).decode('utf-8')[0:22]
        result = TrackModel.query.filter_by(id=track_id).first()
        if result:
            return result, 409
        artista = BASE + "/artists/" + album.artist_id
        albumne = BASE + "/albums/" + album_id
        selfs = BASE + "/tracks/" + track_id
        track = TrackModel(artist_id=album.artist_id, album_id=album_id, id=track_id,
                           name=args['name'], duration=args['duration'], times_played=0, artist=artista, album=albumne, selfs=selfs)
        db.session.add(track)
        db.session.commit()
        return track, 201


class TracksAll(Resource):
    @marshal_with(resource_track_fields)
    def get(self):
        result = TrackModel.query.all()
        return result, 200


class TracksByArtist(Resource):
    @marshal_with(resource_track_fields)
    def get(self, artist_id):
        artist = ArtistModel.query.filter_by(id=artist_id).first()
        if not artist:
            abort(404, message="artista no encontrado")
        result = TrackModel.query.filter_by(artist_id=artist_id).all()
        return result, 200


class TracksId(Resource):
    @marshal_with(resource_track_fields)
    def get(self, track_id):
        result = TrackModel.query.filter_by(id=track_id).first()
        if not result:
            abort(404, message="track no encontrado")
        return result, 200

    def delete(self, track_id):
        result = TrackModel.query.filter_by(id=track_id).first()
        if not result:
            abort(404, message="track no encontrado")
        db.session.delete(result)
        db.session.commit()
        return '', 204


class ReproducirTrack(Resource):
    def put(self, track_id):
        result = TrackModel.query.filter_by(id=track_id).first()
        if not result:
            abort(404, message="canción no encontrada")
        result.times_played = result.times_played + 1
        db.session.commit()
        return '', 200


class ReproducirAlbum(Resource):
    def put(self, album_id):
        album = AlbumModel.query.filter_by(id=album_id).first()
        if not album:
            abort(404, message="álbum no existe")
        result = TrackModel.query.filter_by(album_id=album_id).all()
        for i in range(len(result)):
            result[i].times_played = result[i].times_played + 1
            db.session.commit()
        return '', 200


class ReproducirArtist(Resource):
    def put(self, artist_id):
        artist = ArtistModel.query.filter_by(id=artist_id).first()
        if not artist:
            abort(404, message="artist no existe")
        result = TrackModel.query.filter_by(artist_id=artist_id).all()
        for i in range(len(result)):
            result[i].times_played = result[i].times_played + 1
            db.session.commit()
        return '', 200


api.add_resource(Artist, "/artists")
api.add_resource(ArtistId, "/artists/<artist_id>")
api.add_resource(Albums, "/artists/<artist_id>/albums")
api.add_resource(AlbumsAll, "/albums")
api.add_resource(AlbumsId, "/albums/<album_id>")
api.add_resource(Tracks, "/albums/<album_id>/tracks")
api.add_resource(TracksAll, "/tracks")
api.add_resource(TracksByArtist, "/artists/<artist_id>/tracks")
api.add_resource(TracksId, "/tracks/<track_id>")
api.add_resource(ReproducirTrack, "/tracks/<track_id>/play")
api.add_resource(ReproducirAlbum, "/albums/<album_id>/tracks/play")
api.add_resource(ReproducirArtist, "/artists/<artist_id>/albums/play")
if __name__ == "__main__":
    app.run()
