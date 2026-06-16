from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True)
    password_hash = Column(String(256))
    created_at = Column(DateTime, default=datetime.utcnow)


class CoupleMedia(Base):
    __tablename__ = "couple_media"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(256))
    original_name = Column(String(256))
    file_type = Column(String(20))  # photo / video
    file_path = Column(String(512))
    description = Column(Text, default="")
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class CoupleStory(Base):
    __tablename__ = "couple_stories"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256))
    content = Column(Text)
    mood = Column(String(64), default="romantic")
    created_at = Column(DateTime, default=datetime.utcnow)


class LeetCodeProblem(Base):
    __tablename__ = "leetcode"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True)
    title = Column(String(256))
    difficulty = Column(String(20))  # Easy / Medium / Hard
    tags = Column(String(512))
    description = Column(Text)
    solution = Column(Text)
    reference_url = Column(String(512))


class GitHubRepo(Base):
    __tablename__ = "github_repos"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256))
    url = Column(String(512))
    description = Column(Text)
    language = Column(String(64))
    stars = Column(Integer, default=0)
    category = Column(String(64))


class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512))
    video_id = Column(String(64))
    description = Column(Text)
    category = Column(String(64))


class CryptoPaper(Base):
    __tablename__ = "crypto_papers"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512))
    authors = Column(String(512))
    year = Column(Integer)
    category = Column(String(64))  # symmetric / asymmetric / hash / post_quantum / homomorphic / zkp
    abstract = Column(Text)
    ai_summary = Column(Text)
    url = Column(String(512))
    is_classic = Column(Integer, default=0)


class GNNResource(Base):
    __tablename__ = "gnn_resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512))
    resource_type = Column(String(64))  # paper / code / tutorial
    description = Column(Text)
    url = Column(String(512))
    category = Column(String(64))


class InvestmentResource(Base):
    __tablename__ = "investment_resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512))
    resource_type = Column(String(64))  # stock / fund / crypto / strategy / news
    content = Column(Text)
    url = Column(String(512))
    tags = Column(String(256))


class MakeupResource(Base):
    __tablename__ = "makeup_resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512))
    resource_type = Column(String(64))  # tutorial / product / inspiration
    content = Column(Text)
    url = Column(String(512))
    tags = Column(String(256))


class FashionResource(Base):
    __tablename__ = "fashion_resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512))
    resource_type = Column(String(64))  # outfit / guide / wardrobe
    content = Column(Text)
    url = Column(String(512))
    tags = Column(String(256))


class CookingResource(Base):
    __tablename__ = "cooking_resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512))
    resource_type = Column(String(64))  # recipe / video / nutrition
    content = Column(Text)
    url = Column(String(512))
    tags = Column(String(256))
    difficulty = Column(String(20))
    cook_time = Column(String(32))


class AbroadResource(Base):
    __tablename__ = "abroad_resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512))
    resource_type = Column(String(64))  # school / visa / language / life
    content = Column(Text)
    url = Column(String(512))
    country = Column(String(64))


class CivilResource(Base):
    __tablename__ = "civil_resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512))
    resource_type = Column(String(64))  # xingce / shenlun / interview / current
    content = Column(Text)
    url = Column(String(512))
    year = Column(Integer)
