from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)
    quiz_results: Mapped[list["QuizResult"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    interviews: Mapped[list["Interview"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class QuizResult(Base):
    __tablename__ = "quiz_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    wrong_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    unanswered_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    score_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    time_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    user: Mapped[User] = relationship(back_populates="quiz_results")


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    problem_links: Mapped[list["PlaylistProblem"]] = relationship(
        back_populates="playlist",
        cascade="all, delete-orphan",
        order_by="PlaylistProblem.position",
    )


class Problem(Base):
    __tablename__ = "problems"
    __table_args__ = (
        Index("uq_problem_canonical_key_idx", "canonical_key", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    leetcode_id: Mapped[int] = mapped_column(Integer, nullable=False)
    canonical_key: Mapped[str] = mapped_column(String(1000), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    leetcode_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
    is_premium: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    playlist_links: Mapped[list["PlaylistProblem"]] = relationship(
        back_populates="problem",
        cascade="all, delete-orphan",
    )


class PlaylistProblem(Base):
    __tablename__ = "playlist_problems"
    __table_args__ = (
        UniqueConstraint("playlist_id", "problem_id", name="uq_playlist_problem"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency: Mapped[float] = mapped_column(Float, nullable=False)
    acceptance_rate: Mapped[float] = mapped_column(Float, nullable=False)

    playlist: Mapped[Playlist] = relationship(back_populates="problem_links")
    problem: Mapped[Problem] = relationship(back_populates="playlist_links")


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="in_progress")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="interviews")
    questions: Mapped[list["InterviewQuestion"]] = relationship(
        back_populates="interview", cascade="all, delete-orphan", order_by="InterviewQuestion.position"
    )
    result: Mapped["InterviewResult | None"] = relationship(
        back_populates="interview", cascade="all, delete-orphan", uselist=False
    )


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    __table_args__ = (UniqueConstraint("interview_id", "position", name="uq_interview_question_position"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    kind: Mapped[str] = mapped_column(String(30), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    details_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    interview: Mapped[Interview] = relationship(back_populates="questions")
    answer: Mapped["InterviewAnswer | None"] = relationship(
        back_populates="question", cascade="all, delete-orphan", uselist=False
    )


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    answer_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    self_reported_result: Mapped[str | None] = mapped_column(String(50))
    execution_json: Mapped[str | None] = mapped_column(Text)

    question: Mapped[InterviewQuestion] = relationship(back_populates="answer")


class InterviewResult(Base):
    __tablename__ = "interview_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    dsa_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    sql_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    system_design_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    strengths_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    improvements_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    final_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    interview: Mapped[Interview] = relationship(back_populates="result")
