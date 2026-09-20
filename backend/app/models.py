from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
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
    code_submissions: Mapped[list["CodeSubmission"]] = relationship(
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
    memberships: Mapped[list["PlaylistProblem"]] = relationship(
        back_populates="playlist", cascade="all, delete-orphan", order_by="PlaylistProblem.position"
    )


class Problem(Base):
    __tablename__ = "problems"
    __table_args__ = (UniqueConstraint("canonical_key", name="uq_problem_canonical_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playlist_id: Mapped[int | None] = mapped_column(ForeignKey("playlists.id", ondelete="SET NULL"), nullable=True, index=True)
    leetcode_id: Mapped[int] = mapped_column(Integer, nullable=False)
    canonical_key: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    leetcode_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False)
    acceptance_rate: Mapped[float] = mapped_column(Float, nullable=False)
    frequency: Mapped[float] = mapped_column(Float, nullable=False)
    is_premium: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=None)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    playlist: Mapped[Playlist | None] = relationship()
    memberships: Mapped[list["PlaylistProblem"]] = relationship(back_populates="problem", cascade="all, delete-orphan")
    test_cases: Mapped[list["ProblemTestCase"]] = relationship(
        back_populates="problem",
        cascade="all, delete-orphan",
        order_by="ProblemTestCase.position",
    )
    execution_spec: Mapped["ProblemExecutionSpec | None"] = relationship(
        back_populates="problem",
        uselist=False,
        cascade="all, delete-orphan",
    )
    code_submissions: Mapped[list["CodeSubmission"]] = relationship(
        back_populates="problem",
        cascade="all, delete-orphan",
    )


class ProblemTestCase(Base):
    __tablename__ = "problem_test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    input_data: Mapped[str] = mapped_column(String(10000), nullable=False)
    expected_output: Mapped[str] = mapped_column(String(10000), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False, default="custom")
    difficulty_level: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    explanation: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    is_sample: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    problem: Mapped[Problem] = relationship(back_populates="test_cases")


class PlaylistProblem(Base):
    __tablename__ = "playlist_problems"
    __table_args__ = (UniqueConstraint("playlist_id", "problem_id", name="uq_playlist_problem"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency: Mapped[float] = mapped_column(Float, nullable=False)
    acceptance_rate: Mapped[float] = mapped_column(Float, nullable=False)

    playlist: Mapped[Playlist] = relationship(back_populates="memberships")
    problem: Mapped[Problem] = relationship(back_populates="memberships")


class ProblemExecutionSpec(Base):
    __tablename__ = "problem_execution_specs"
    __table_args__ = (UniqueConstraint("problem_id", "language", name="uq_execution_spec_problem_language"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    execution_type: Mapped[str] = mapped_column(String(30), nullable=False)
    function_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    starter_code: Mapped[str] = mapped_column(Text, nullable=False)
    input_format: Mapped[str] = mapped_column(String(1000), nullable=False, default="JSON arguments")
    output_format: Mapped[str] = mapped_column(String(1000), nullable=False, default="JSON")
    output_comparison: Mapped[str] = mapped_column(String(30), nullable=False, default="exact_json")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    problem: Mapped[Problem] = relationship(back_populates="execution_spec")


class ProblemReferenceSolution(Base):
    __tablename__ = "problem_reference_solutions"
    __table_args__ = (UniqueConstraint("problem_id", "language", name="uq_reference_solution_problem_language"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    validated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))


class CodeSubmission(Base):
    __tablename__ = "code_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True
    )
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    passed_tests: Mapped[int] = mapped_column(Integer, nullable=False)
    total_tests: Mapped[int] = mapped_column(Integer, nullable=False)
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    user: Mapped[User] = relationship(back_populates="code_submissions")
    problem: Mapped[Problem] = relationship(back_populates="code_submissions")
