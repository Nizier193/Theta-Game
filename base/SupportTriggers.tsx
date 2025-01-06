<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.10" tiledversion="1.11.0" name="SupportTriggers" tilewidth="50" tileheight="50" tilecount="1" columns="0">
 <grid orientation="orthogonal" width="1" height="1"/>
 <tile id="0">
  <properties>
   <property name="CameraMovement" value="Move"/>
   <property name="IsTrigger" type="bool" value="true"/>
   <property name="ObjectType" value="Trigger"/>
   <property name="OffsetX" type="int" value="0"/>
   <property name="OffsetY" type="int" value="0"/>
   <property name="ToX" type="int" value="0"/>
   <property name="ToY" type="int" value="0"/>
   <property name="TriggerType" value="CameraControl"/>
  </properties>
  <image source="textures/images/camera_point.png" width="50" height="50"/>
 </tile>
</tileset>
