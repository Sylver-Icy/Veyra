"""
Profile API Routes

This file exposes HTTP endpoints related to user profile data
such as energy and friendship status.
Routes are thin. They validate input, call services, and return schemas.
"""

from fastapi import APIRouter

from services.jobs_services import JobsClass
from services.friendship_services import check_friendship
from api.schemas import EnergyResponse, FriendshipResponse


router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)


@router.get(
    "/{user_id}/energy",
    response_model=EnergyResponse,
)
def get_energy(user_id: int):
    jobs = JobsClass(user_id)
    current, maximum = jobs.check_energy()

    return EnergyResponse(
        user_id=user_id,
        current=current,
        maximum=maximum,
    )


@router.get(
    "/{user_id}/friendship",
    response_model=FriendshipResponse,
)
def get_friendship(user_id: int):
    title, progress = check_friendship(user_id)

    return FriendshipResponse(
        user_id=user_id,
        title=title,
        progress=progress,
    )